from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from typing import Dict, Any, List, Optional
import json

from app.models import (
    RawMarketPrice,
    CleanedMarketPrice,
    Market,
    Commodity,
    MarketAlias,
    DataQualityReport
)
from app.utils.market_normalization import normalizer
from app.utils.date_utils import parse_date, is_future_date
from app.utils.validation import clean_numeric, validate_price_relationship

def run_cleaning_pipeline(db: Session) -> Dict[str, Any]:
    raw_records = db.query(RawMarketPrice).all()
    
    total_input_rows = len(raw_records)
    valid_rows = 0
    invalid_rows = 0
    missing_value_counts = {"modal_price": 0, "arrival_quantity": 0, "date": 0}
    duplicate_count = 0
    suspicious_price_count = 0
    future_date_count = 0
    
    records_per_commodity = {}
    records_per_market = {}
    records_per_pair = {}
    observations_per_year = {}
    
    market_cache: Dict[str, Market] = {}
    commodity_cache: Dict[str, Commodity] = {}
    seen_unique_keys = set()
    
    # Pre-populate market cache
    for m in db.query(Market).all():
        market_cache[m.canonical_name] = m
    for c in db.query(Commodity).all():
        commodity_cache[c.canonical_name] = c

    cleaned_objects = []
    
    for raw in raw_records:
        # 1. Date validation
        obs_date = parse_date(raw.observation_date)
        if not obs_date:
            invalid_rows += 1
            missing_value_counts["date"] += 1
            continue
            
        if is_future_date(obs_date):
            future_date_count += 1
            invalid_rows += 1
            continue

        # 2. Market normalization
        canonical_market_name, market_info = normalizer.normalize_market(raw.original_market)
        district = normalizer.normalize_district(raw.district)
        
        if canonical_market_name not in market_cache:
            lat = market_info.get("latitude") if market_info else None
            lon = market_info.get("longitude") if market_info else None
            new_market = Market(
                canonical_name=canonical_market_name,
                original_name=raw.original_market or canonical_market_name,
                district=district,
                state=raw.state or "Andhra Pradesh",
                latitude=lat,
                longitude=lon
            )
            db.add(new_market)
            db.flush()
            market_cache[canonical_market_name] = new_market
            
            # Save alias if original name differs
            if raw.original_market and raw.original_market != canonical_market_name:
                alias = MarketAlias(
                    original_name=raw.original_market,
                    canonical_market_id=new_market.id,
                    confidence=1.0
                )
                db.add(alias)
        
        market_obj = market_cache[canonical_market_name]

        # 3. Commodity normalization
        canonical_comm_name = normalizer.normalize_commodity(raw.original_commodity)
        if canonical_comm_name not in commodity_cache:
            new_comm = Commodity(
                canonical_name=canonical_comm_name,
                original_name=raw.original_commodity or canonical_comm_name,
                commodity_group=raw.commodity_group or "Vegetables",
                unit="₹ per quintal"
            )
            db.add(new_comm)
            db.flush()
            commodity_cache[canonical_comm_name] = new_comm
            
        comm_obj = commodity_cache[canonical_comm_name]

        # 4. Numeric cleaning
        modal_p = clean_numeric(raw.modal_price_raw)
        min_p = clean_numeric(raw.min_price_raw)
        max_p = clean_numeric(raw.max_price_raw)
        arrival_q = clean_numeric(raw.arrival_quantity_raw)

        if modal_p is None or modal_p <= 0:
            missing_value_counts["modal_price"] += 1
            invalid_rows += 1
            continue

        if arrival_q is None:
            missing_value_counts["arrival_quantity"] += 1

        # 5. Price relationship validation
        is_rel_valid, warning_reason = validate_price_relationship(min_p, modal_p, max_p)
        quality_status = "valid"
        suspicious = False
        
        if not is_rel_valid:
            suspicious_price_count += 1
            suspicious = True
            quality_status = "suspicious"
            # Swap or cap if needed or retain with warning
            if min_p and max_p and min_p > max_p:
                min_p, max_p = max_p, min_p

        # 6. Deduplication check
        unique_key = (market_obj.id, comm_obj.id, obs_date)
        if unique_key in seen_unique_keys:
            duplicate_count += 1
            continue
        seen_unique_keys.add(unique_key)

        # Build cleaned record
        cleaned_rec = CleanedMarketPrice(
            market_id=market_obj.id,
            commodity_id=comm_obj.id,
            observation_date=obs_date,
            arrival_quantity=arrival_q,
            min_price=min_p if min_p is not None else modal_p,
            modal_price=modal_p,
            max_price=max_p if max_p is not None else modal_p,
            unit=comm_obj.unit,
            arrival_missing=(arrival_q is None),
            price_missing=False,
            suspicious_record=suspicious,
            quality_status=quality_status,
            source_raw_id=raw.id
        )
        cleaned_objects.append(cleaned_rec)
        valid_rows += 1

        # Report stats tracking
        records_per_commodity[canonical_comm_name] = records_per_commodity.get(canonical_comm_name, 0) + 1
        records_per_market[canonical_market_name] = records_per_market.get(canonical_market_name, 0) + 1
        pair_key = f"{canonical_market_name} | {canonical_comm_name}"
        records_per_pair[pair_key] = records_per_pair.get(pair_key, 0) + 1
        
        year_str = str(obs_date.year)
        observations_per_year[year_str] = observations_per_year.get(year_str, 0) + 1

    # Clear old cleaned prices to ensure fresh sync
    db.query(CleanedMarketPrice).delete()
    db.bulk_save_objects(cleaned_objects)
    
    # Date range
    all_dates = [c.observation_date for c in cleaned_objects]
    min_date = str(min(all_dates)) if all_dates else None
    max_date = str(max(all_dates)) if all_dates else None

    report_data = {
        "total_input_rows": total_input_rows,
        "valid_rows": valid_rows,
        "invalid_rows": invalid_rows,
        "missing_value_counts": missing_value_counts,
        "duplicate_counts": duplicate_count,
        "suspicious_price_counts": suspicious_price_count,
        "future_date_counts": future_date_count,
        "records_per_commodity": records_per_commodity,
        "records_per_market": records_per_market,
        "records_per_pair": records_per_pair,
        "date_range": {"start": min_date, "end": max_date},
        "observations_per_year": observations_per_year
    }

    quality_report = DataQualityReport(
        file_name="master-data.csv",
        source="csv_upload & api",
        report_json=report_data
    )
    db.add(quality_report)
    db.commit()

    return report_data
