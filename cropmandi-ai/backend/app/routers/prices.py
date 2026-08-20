import logging
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Union
from datetime import date, datetime, timedelta
from app.database import get_db
from app.config import settings
from app.models import Market, Commodity, OfficialMarketPrice
from app.schemas.price import (
    LatestPriceOut,
    PriceHistoryItem,
    TrendPointOut,
    CompareMarketOut,
    ExcludedMarketOut,
    CompareResponseOut,
    PriceCompareItem,
)
from app.services.master_data_service import load_master_data
from app.utils.market_normalization import normalize_market_name, normalize_commodity_name
from app.utils.date_service import get_ist_today, parse_internal_date

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/prices", tags=["Prices"])

ALLOWED_SOURCES = {"official_api", "official_database", "official_csv"}
BLOCKED_SOURCES = {
    "predicted",
    "predicted_model",
    "fallback_last_observed",
    "fallback_rolling_average",
    "unavailable"
}


def _get_source_label(source: str) -> str:
    if source == "official_api":
        return "Official API value"
    elif source == "official_database":
        return "Stored official value"
    elif source == "official_csv":
        return "Official value from master data"
    return "Official observed value"


@router.get("/latest", response_model=LatestPriceOut)
def get_latest_price(
    market_id: int = Query(...),
    commodity_id: int = Query(...),
    db: Session = Depends(get_db)
):
    market = db.query(Market).get(market_id)
    commodity = db.query(Commodity).get(commodity_id)
    if not market or not commodity:
        raise HTTPException(status_code=404, detail="Market or Commodity not found")

    target_m = normalize_market_name(market.canonical_name).lower()
    target_orig_m = normalize_market_name(market.original_name or "").lower()
    target_c = normalize_commodity_name(commodity.canonical_name).lower()

    master_idx = load_master_data()

    matching_records = []
    if settings.SHOW_CSV_IN_TRENDS:
        for (c, m, d_str), rec in master_idx.items():
            if c == target_c and (m == target_m or m == target_orig_m):
                matching_records.append((d_str, rec, "official_csv"))

    # Also check DB OfficialMarketPrice
    db_recs = db.query(OfficialMarketPrice).filter(
        OfficialMarketPrice.market_id == market_id,
        OfficialMarketPrice.commodity_id == commodity_id
    ).order_by(OfficialMarketPrice.observation_date.desc()).all()

    for r in db_recs:
        d_str = r.observation_date.strftime("%Y-%m-%d") if isinstance(r.observation_date, (date, datetime)) else str(r.observation_date)
        matching_records.append((d_str, {
            "modal_price": r.modal_price,
            "min_price": r.min_price,
            "max_price": r.max_price,
            "arrival_quantity": r.arrival_quantity,
            "unit": r.unit
        }, "official_database"))

    if not matching_records:
        raise HTTPException(status_code=404, detail="No authentic price records found for the given market and commodity")

    matching_records.sort(key=lambda x: x[0])
    latest_date_str, latest_rec, _ = matching_records[-1]

    modal_p = float(latest_rec.get("modal_price", 0))
    min_p = float(latest_rec.get("min_price", round(modal_p * 0.95, 2))) if latest_rec.get("min_price") is not None else round(modal_p * 0.95, 2)
    max_p = float(latest_rec.get("max_price", round(modal_p * 1.05, 2))) if latest_rec.get("max_price") is not None else round(modal_p * 1.05, 2)
    arr_q = float(latest_rec.get("arrival_quantity", 0)) if latest_rec.get("arrival_quantity") is not None else None

    return LatestPriceOut(
        market_id=market.id,
        market_name=market.canonical_name,
        district=market.district,
        commodity_id=commodity.id,
        commodity_name=commodity.canonical_name,
        observation_date=latest_date_str,
        modal_price=modal_p,
        min_price=min_p,
        max_price=max_p,
        arrival_quantity=arr_q,
        unit=commodity.unit or "Rs./Quintal"
    )


@router.get("/trends", response_model=List[TrendPointOut])
@router.get("/history", response_model=List[TrendPointOut])
def get_price_trends(
    market: Optional[str] = Query(None),
    market_id: Optional[int] = Query(None),
    commodity: Optional[str] = Query(None),
    commodity_id: Optional[int] = Query(None),
    state: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: Optional[int] = Query(None),
    force_refresh: bool = Query(True),
    db: Session = Depends(get_db)
):
    # Sanitize parameter types for direct Python / testing calls
    if not isinstance(commodity_id, int):
        commodity_id = None
    if not isinstance(commodity, str):
        commodity = None
    if not isinstance(market_id, int):
        market_id = None
    if not isinstance(market, str):
        market = None
    if not isinstance(state, str):
        state = None
    if not isinstance(district, str):
        district = None
    if not isinstance(days, int) or days <= 0:
        days = 30
    if not isinstance(start_date, str):
        start_date = None
    if not isinstance(end_date, str):
        end_date = None
    if not isinstance(limit, int):
        limit = None
    if not isinstance(force_refresh, bool):
        force_refresh = True

    # 1. Resolve Commodity
    comm_obj = None
    if commodity_id:
        comm_obj = db.query(Commodity).get(commodity_id)
    elif commodity:
        if str(commodity).isdigit():
            comm_obj = db.query(Commodity).get(int(commodity))
        if not comm_obj:
            comm_obj = db.query(Commodity).filter(
                (Commodity.canonical_name.ilike(f"%{commodity}%")) | (Commodity.original_name.ilike(f"%{commodity}%"))
            ).first()

    # 2. Resolve Market
    market_obj = None
    if market_id:
        market_obj = db.query(Market).get(market_id)
    elif market:
        if str(market).isdigit():
            market_obj = db.query(Market).get(int(market))
        if not market_obj:
            market_obj = db.query(Market).filter(
                (Market.canonical_name.ilike(f"%{market}%")) | (Market.original_name.ilike(f"%{market}%"))
            ).first()

    if not comm_obj or not market_obj:
        return []

    # 3. Time Window Calculation (Asia/Kolkata current date)
    today = get_ist_today()
    if end_date:
        d_end = parse_internal_date(end_date) or today
    else:
        d_end = today

    effective_days = limit if limit and limit > 0 else days
    if start_date:
        d_start = parse_internal_date(start_date) or (d_end - timedelta(days=effective_days - 1))
    else:
        d_start = d_end - timedelta(days=effective_days - 1)

    target_m = normalize_market_name(market_obj.canonical_name).lower()
    target_orig_m = normalize_market_name(market_obj.original_name or "").lower()
    target_c = normalize_commodity_name(comm_obj.canonical_name).lower()

    # 4. Optional Live API Refresh for this crop and market in the 30-day window
    if force_refresh:
        try:
            from app.services.official_market_service import fetch_date_range_records
            fetch_date_range_records(
                db=db,
                commodity=comm_obj.canonical_name,
                market=market_obj.canonical_name,
                start_date=d_start,
                end_date=d_end,
                district=market_obj.district,
                state=market_obj.state
            )
        except Exception as e:
            logger.debug("Live API refresh in trends skipped/failed: %s", e)

    # 5. Collect authentic records
    records_by_date = {}

    # Source 3: master-data.csv (if within allowed recency period & enabled)
    if settings.SHOW_CSV_IN_TRENDS:
        master_idx = load_master_data()
        for (c, m, d_str), rec in master_idx.items():
            if c == target_c and (m == target_m or m == target_orig_m):
                try:
                    d = datetime.strptime(d_str, "%Y-%m-%d").date()
                    if d_start <= d <= d_end:
                        p_val = float(rec.get("modal_price", 0))
                        if p_val > 0:
                            age = (today - d).days
                            records_by_date[d_str] = TrendPointOut(
                                date=d_str,
                                modal_price=p_val,
                                min_price=float(rec.get("min_price")) if rec.get("min_price") is not None else round(p_val * 0.95, 2),
                                max_price=float(rec.get("max_price")) if rec.get("max_price") is not None else round(p_val * 1.05, 2),
                                arrival_quantity=float(rec.get("arrival_quantity", 0)) if rec.get("arrival_quantity") is not None else None,
                                unit=comm_obj.unit or "Rs./Quintal",
                                price_source="official_csv",
                                is_observed=True,
                                is_predicted=False,
                                data_age_days=age,
                                source_label=_get_source_label("official_csv"),
                                observed_at=d_str
                            )
                except Exception:
                    pass

    # Source 2 & 1: Stored Official Records & Fresh Official API Records in Database
    try:
        db_recs = db.query(OfficialMarketPrice).filter(
            OfficialMarketPrice.market_id == market_obj.id,
            OfficialMarketPrice.commodity_id == comm_obj.id,
            OfficialMarketPrice.observation_date >= d_start,
            OfficialMarketPrice.observation_date <= d_end
        ).all()

        for r in db_recs:
            d_str = r.observation_date.strftime("%Y-%m-%d") if isinstance(r.observation_date, (date, datetime)) else str(r.observation_date)
            p_val = float(r.modal_price)
            if p_val > 0:
                obs_d = r.observation_date if isinstance(r.observation_date, date) else datetime.strptime(d_str, "%Y-%m-%d").date()
                age = (today - obs_d).days
                src = "official_api" if age <= 3 else "official_database"
                records_by_date[d_str] = TrendPointOut(
                    date=d_str,
                    modal_price=p_val,
                    min_price=float(r.min_price) if r.min_price is not None else round(p_val * 0.95, 2),
                    max_price=float(r.max_price) if r.max_price is not None else round(p_val * 1.05, 2),
                    arrival_quantity=float(r.arrival_quantity) if r.arrival_quantity is not None else None,
                    unit=r.unit or comm_obj.unit or "Rs./Quintal",
                    price_source=src,
                    is_observed=True,
                    is_predicted=False,
                    data_age_days=age,
                    source_label=_get_source_label(src),
                    observed_at=d_str
                )
    except Exception as e:
        logger.debug("Querying DB official records error: %s", e)

    # 6. Sort ascending by date and enforce source filtering
    final_points: List[TrendPointOut] = []
    for d_str in sorted(records_by_date.keys()):
        pt = records_by_date[d_str]
        # Data integrity check
        if pt.price_source not in ALLOWED_SOURCES or pt.is_predicted or not pt.is_observed:
            continue
        final_points.append(pt)

    return final_points


@router.get("/compare", response_model=CompareResponseOut)
def compare_market_prices(
    commodity: Optional[str] = Query(None),
    commodity_id: Optional[int] = Query(None),
    state: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    date: Optional[str] = Query(None, alias="date"),
    max_age_days: int = Query(7, ge=1, le=365),
    force_refresh: bool = Query(True),
    db: Session = Depends(get_db)
):
    # Sanitize parameter types for direct Python / testing calls
    if not isinstance(commodity_id, int):
        commodity_id = None
    if not isinstance(commodity, str):
        commodity = None
    if not isinstance(state, str):
        state = None
    if not isinstance(district, str):
        district = None
    if not isinstance(date, str):
        date = None
    if not isinstance(max_age_days, int) or max_age_days <= 0:
        max_age_days = 7
    if not isinstance(force_refresh, bool):
        force_refresh = True

    # 1. Resolve Commodity
    comm_obj = None
    if commodity_id:
        comm_obj = db.query(Commodity).get(commodity_id)
    elif commodity:
        if str(commodity).isdigit():
            comm_obj = db.query(Commodity).get(int(commodity))
        if not comm_obj:
            comm_obj = db.query(Commodity).filter(
                (Commodity.canonical_name.ilike(f"%{commodity}%")) | (Commodity.original_name.ilike(f"%{commodity}%"))
            ).first()

    if not comm_obj:
        comm_obj = db.query(Commodity).filter(Commodity.is_active == True).first()

    if not comm_obj:
        return CompareResponseOut(
            commodity="Unknown",
            requested_date=date,
            current_date=get_ist_today().strftime("%Y-%m-%d"),
            max_latest_value_age_days=max_age_days,
            markets=[],
            excluded_markets=[]
        )

    today = get_ist_today()
    req_date_obj = parse_internal_date(date) if date else None
    cutoff_date = (req_date_obj or today) - timedelta(days=max_age_days)

    target_c = normalize_commodity_name(comm_obj.canonical_name).lower()

    # Pre-cache DB markets
    all_markets = db.query(Market).filter(Market.is_active == True).all()
    market_lookup = {}
    for m in all_markets:
        market_lookup[normalize_market_name(m.canonical_name).lower()] = m
        if m.original_name:
            market_lookup[normalize_market_name(m.original_name).lower()] = m

    # 2. Collect all observed records per market
    market_records = {}

    # Check master-data.csv
    if settings.SHOW_CSV_IN_COMPARISON:
        master_idx = load_master_data()
        for (c, m, d_str), rec in master_idx.items():
            if c == target_c:
                try:
                    d = datetime.strptime(d_str, "%Y-%m-%d").date()
                    if req_date_obj and d > req_date_obj:
                        continue
                    p_val = float(rec.get("modal_price", 0))
                    if p_val > 0:
                        if m not in market_records or d > market_records[m]["date"]:
                            m_db = market_lookup.get(m)
                            market_records[m] = {
                                "market_name": m_db.canonical_name if m_db else m.title(),
                                "market_id": m_db.id if m_db else None,
                                "district": m_db.district if m_db else rec.get("district", "Andhra Pradesh"),
                                "state": m_db.state if m_db else rec.get("state", "Andhra Pradesh"),
                                "date": d,
                                "modal_price": p_val,
                                "min_price": float(rec.get("min_price")) if rec.get("min_price") is not None else round(p_val * 0.95, 2),
                                "max_price": float(rec.get("max_price")) if rec.get("max_price") is not None else round(p_val * 1.05, 2),
                                "arrival_quantity": float(rec.get("arrival_quantity", 0)) if rec.get("arrival_quantity") is not None else None,
                                "price_source": "official_csv",
                                "unit": comm_obj.unit or "Rs./Quintal"
                            }
                except Exception:
                    pass

    # Check DB OfficialMarketPrice
    try:
        db_recs = db.query(OfficialMarketPrice).filter(
            OfficialMarketPrice.commodity_id == comm_obj.id
        ).all()

        for r in db_recs:
            m_db = db.query(Market).get(r.market_id)
            if not m_db:
                continue
            norm_m = normalize_market_name(m_db.canonical_name).lower()
            obs_d = r.observation_date if isinstance(r.observation_date, date) else datetime.strptime(str(r.observation_date), "%Y-%m-%d").date()

            if req_date_obj and obs_d > req_date_obj:
                continue

            p_val = float(r.modal_price)
            if p_val > 0:
                if norm_m not in market_records or obs_d > market_records[norm_m]["date"]:
                    age = (today - obs_d).days
                    src = "official_api" if age <= 3 else "official_database"
                    market_records[norm_m] = {
                        "market_name": m_db.canonical_name,
                        "market_id": m_db.id,
                        "district": m_db.district,
                        "state": m_db.state,
                        "date": obs_d,
                        "modal_price": p_val,
                        "min_price": float(r.min_price) if r.min_price is not None else round(p_val * 0.95, 2),
                        "max_price": float(r.max_price) if r.max_price is not None else round(p_val * 1.05, 2),
                        "arrival_quantity": float(r.arrival_quantity) if r.arrival_quantity is not None else None,
                        "price_source": src,
                        "unit": r.unit or comm_obj.unit or "Rs./Quintal"
                    }
    except Exception as e:
        logger.debug("Compare DB query error: %s", e)

    # 3. Categorize into active comparison vs excluded
    included_markets: List[CompareMarketOut] = []
    excluded_markets: List[ExcludedMarketOut] = []

    for m_key, rec in market_records.items():
        obs_date = rec["date"]
        data_age = (today - obs_date).days
        m_name = rec["market_name"]

        # District / State filters
        if district and district.lower() not in rec["district"].lower():
            continue
        if state and state.lower() not in rec["state"].lower():
            continue

        if data_age <= max_age_days:
            included_markets.append(CompareMarketOut(
                market=m_name,
                district=rec["district"],
                state=rec["state"],
                modal_price=rec["modal_price"],
                min_price=rec["min_price"],
                max_price=rec["max_price"],
                arrival_quantity=rec["arrival_quantity"],
                observation_date=obs_date.strftime("%Y-%m-%d"),
                data_age_days=data_age,
                price_source=rec["price_source"],
                is_observed=True,
                is_predicted=False,
                source_label=_get_source_label(rec["price_source"]),
                is_latest_available_value=True,
                unit=rec["unit"],
                market_id=rec["market_id"]
            ))
        else:
            excluded_markets.append(ExcludedMarketOut(
                market=m_name,
                reason=f"No official observed price in the recent allowed period (latest was {obs_date.strftime('%Y-%m-%d')}, age: {data_age} days > {max_age_days}).",
                latest_observation_date=obs_date.strftime("%Y-%m-%d"),
                data_age_days=data_age
            ))

    return CompareResponseOut(
        commodity=comm_obj.canonical_name,
        requested_date=date,
        current_date=today.strftime("%Y-%m-%d"),
        max_latest_value_age_days=max_age_days,
        markets=sorted(included_markets, key=lambda x: x.market),
        excluded_markets=sorted(excluded_markets, key=lambda x: x.market)
    )


