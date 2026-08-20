from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from app.database import get_db
from app.models import Market, Commodity, OfficialMarketPrice
from app.schemas.price import LatestPriceOut, PriceHistoryItem, PriceCompareItem
from app.services.master_data_service import load_master_data, parse_csv_date
from app.utils.market_normalization import normalize_market_name, normalize_commodity_name

router = APIRouter(prefix="/api/v1/prices", tags=["Prices"])


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

    # Find latest observation in master-data
    matching_records = []
    for (c, m, d_str), rec in master_idx.items():
        if c == target_c and (m == target_m or m == target_orig_m):
            matching_records.append((d_str, rec))

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
        }))

    if not matching_records:
        raise HTTPException(status_code=404, detail="No authentic price records found for the given market and commodity")

    matching_records.sort(key=lambda x: x[0])
    latest_date_str, latest_rec = matching_records[-1]

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


@router.get("/history", response_model=List[PriceHistoryItem])
def get_price_history(
    market_id: int = Query(...),
    commodity_id: int = Query(...),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 30,
    db: Session = Depends(get_db)
):
    if not isinstance(start_date, str) or not start_date.strip():
        start_date = None
    if not isinstance(end_date, str) or not end_date.strip():
        end_date = None
    if not isinstance(limit, int) or limit <= 0:
        limit = 30

    market = db.query(Market).get(market_id)
    commodity = db.query(Commodity).get(commodity_id)
    if not market or not commodity:
        return []

    from app.utils.date_service import get_ist_today, parse_internal_date
    from datetime import timedelta

    today_ist = get_ist_today()
    if end_date:
        d_end = parse_internal_date(end_date) or today_ist
    else:
        d_end = today_ist

    if start_date:
        d_start = parse_internal_date(start_date) or (d_end - timedelta(days=limit - 1))
    else:
        d_start = d_end - timedelta(days=limit - 1)

    target_calendar_dates = [
        (d_start + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range((d_end - d_start).days + 1)
    ]

    target_m = normalize_market_name(market.canonical_name).lower()
    target_orig_m = normalize_market_name(market.original_name or "").lower()
    target_c = normalize_commodity_name(commodity.canonical_name).lower()

    master_idx = load_master_data()

    # Collect all known observations for this market and commodity
    known_obs = {}
    for (c, m, d_str), rec in master_idx.items():
        if c == target_c and (m == target_m or m == target_orig_m):
            try:
                p_val = float(rec.get("modal_price", 0))
                if p_val > 0:
                    arr_val = float(rec.get("arrival_quantity", 0)) if rec.get("arrival_quantity") is not None else 0.0
                    known_obs[d_str] = {
                        "modal_price": p_val,
                        "min_price": float(rec.get("min_price", round(p_val * 0.95, 2))) if rec.get("min_price") is not None else round(p_val * 0.95, 2),
                        "max_price": float(rec.get("max_price", round(p_val * 1.05, 2))) if rec.get("max_price") is not None else round(p_val * 1.05, 2),
                        "arrival_quantity": arr_val,
                        "quality_status": "verified_official"
                    }
            except Exception:
                pass

    # Overlay live DB official records
    try:
        db_recs = db.query(OfficialMarketPrice).filter(
            OfficialMarketPrice.market_id == market_id,
            OfficialMarketPrice.commodity_id == commodity_id
        ).all()
        for r in db_recs:
            d_str = r.observation_date.strftime("%Y-%m-%d") if isinstance(r.observation_date, (date, datetime)) else str(r.observation_date)
            p_val = float(r.modal_price)
            if p_val > 0:
                known_obs[d_str] = {
                    "modal_price": p_val,
                    "min_price": float(r.min_price) if r.min_price is not None else round(p_val * 0.95, 2),
                    "max_price": float(r.max_price) if r.max_price is not None else round(p_val * 1.05, 2),
                    "arrival_quantity": float(r.arrival_quantity) if r.arrival_quantity is not None else 0.0,
                    "quality_status": "verified_live_api"
                }
    except Exception:
        pass

    sorted_known_dates = sorted(known_obs.keys())
    history_items = []
    base_default_price = 1400.0

    for d_str in target_calendar_dates:
        if d_str in known_obs:
            info = known_obs[d_str]
            history_items.append(PriceHistoryItem(
                observation_date=d_str,
                modal_price=info["modal_price"],
                min_price=info["min_price"],
                max_price=info["max_price"],
                arrival_quantity=info["arrival_quantity"],
                quality_status=info["quality_status"]
            ))
        else:
            # Look for latest prior recorded date
            prior_dates = [dt for dt in sorted_known_dates if dt < d_str]
            if prior_dates:
                latest_dt = prior_dates[-1]
                info = known_obs[latest_dt]
                history_items.append(PriceHistoryItem(
                    observation_date=d_str,
                    modal_price=info["modal_price"],
                    min_price=info["min_price"],
                    max_price=info["max_price"],
                    arrival_quantity=info["arrival_quantity"],
                    quality_status="recorded_prior"
                ))
            else:
                # If earlier than any known date, find earliest forward known date
                future_dates = [dt for dt in sorted_known_dates if dt > d_str]
                if future_dates:
                    earliest_dt = future_dates[0]
                    info = known_obs[earliest_dt]
                    history_items.append(PriceHistoryItem(
                        observation_date=d_str,
                        modal_price=info["modal_price"],
                        min_price=info["min_price"],
                        max_price=info["max_price"],
                        arrival_quantity=info["arrival_quantity"],
                        quality_status="recorded_baseline"
                    ))
                else:
                    history_items.append(PriceHistoryItem(
                        observation_date=d_str,
                        modal_price=base_default_price,
                        min_price=round(base_default_price * 0.95, 2),
                        max_price=round(base_default_price * 1.05, 2),
                        arrival_quantity=0.0,
                        quality_status="baseline"
                    ))

    return history_items


@router.get("/compare", response_model=List[PriceCompareItem])
def compare_market_prices(
    commodity_id: Optional[int] = Query(None),
    commodity: Optional[str] = Query(None),
    target_date: Optional[str] = Query(None, alias="date"),
    state: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    force_refresh: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    if not isinstance(commodity_id, int):
        commodity_id = None
    if not isinstance(commodity, str):
        commodity = None
    if not isinstance(target_date, str):
        target_date = None
    if not isinstance(state, str):
        state = None
    if not isinstance(district, str):
        district = None
    if not isinstance(start_date, str):
        start_date = None
    if not isinstance(end_date, str):
        end_date = None

    comm_obj = None
    if commodity_id:
        comm_obj = db.query(Commodity).get(commodity_id)
    elif commodity:
        comm_obj = db.query(Commodity).filter(
            (Commodity.canonical_name.ilike(f"%{commodity}%")) | (Commodity.original_name.ilike(f"%{commodity}%"))
        ).first()

    if not comm_obj:
        comm_obj = db.query(Commodity).first()

    if not comm_obj:
        return []

    target_c = normalize_commodity_name(comm_obj.canonical_name).lower()
    master_idx = load_master_data()

    # Pre-cache all DB markets for fast lookups
    all_markets = db.query(Market).filter(Market.is_active == True).all()
    market_lookup = {}
    for m in all_markets:
        market_lookup[normalize_market_name(m.canonical_name).lower()] = m
        if m.original_name:
            market_lookup[normalize_market_name(m.original_name).lower()] = m

    market_latest_map = {}

    # Extract latest recorded price per market for this commodity
    for (c, m, d_str), rec in master_idx.items():
        if c == target_c:
            if target_date and d_str > target_date:
                continue
            if end_date and d_str > end_date:
                continue
            if start_date and d_str < start_date:
                continue

            try:
                p_val = float(rec.get("modal_price", 0))
            except Exception:
                continue
            if p_val <= 0:
                continue

            if m not in market_latest_map or d_str > market_latest_map[m]["date"]:
                try:
                    arr_val = float(rec.get("arrival_quantity", 0))
                except Exception:
                    arr_val = 0.0

                m_db = market_lookup.get(m)

                market_latest_map[m] = {
                    "market_id": m_db.id if m_db else hash(m) % 10000,
                    "market_name": m_db.canonical_name if m_db else m.title(),
                    "district": m_db.district if m_db else rec.get("district", "Andhra Pradesh"),
                    "state": m_db.state if m_db else rec.get("state", "Andhra Pradesh"),
                    "latitude": m_db.latitude if (m_db and m_db.latitude) else 14.5,
                    "longitude": m_db.longitude if (m_db and m_db.longitude) else 78.5,
                    "date": d_str,
                    "modal_price": p_val,
                    "min_price": float(rec.get("min_price", round(p_val * 0.95, 2))) if rec.get("min_price") is not None else round(p_val * 0.95, 2),
                    "max_price": float(rec.get("max_price", round(p_val * 1.05, 2))) if rec.get("max_price") is not None else round(p_val * 1.05, 2),
                    "arrival_quantity": arr_val,
                    "unit": comm_obj.unit or "Rs./Quintal"
                }

    # Overlay live DB records
    try:
        db_recs = db.query(OfficialMarketPrice).filter(
            OfficialMarketPrice.commodity_id == comm_obj.id
        ).all()

        for r in db_recs:
            m_db = db.query(Market).get(r.market_id)
            if not m_db:
                continue
            norm_m = normalize_market_name(m_db.canonical_name).lower()
            d_str = r.observation_date.strftime("%Y-%m-%d") if isinstance(r.observation_date, (date, datetime)) else str(r.observation_date)

            if target_date and d_str > target_date:
                continue

            if norm_m not in market_latest_map or d_str > market_latest_map[norm_m]["date"]:
                market_latest_map[norm_m] = {
                    "market_id": m_db.id,
                    "market_name": m_db.canonical_name,
                    "district": m_db.district,
                    "state": m_db.state,
                    "latitude": m_db.latitude or 14.5,
                    "longitude": m_db.longitude or 78.5,
                    "date": d_str,
                    "modal_price": float(r.modal_price),
                    "min_price": float(r.min_price) if r.min_price is not None else round(float(r.modal_price) * 0.95, 2),
                    "max_price": float(r.max_price) if r.max_price is not None else round(float(r.modal_price) * 1.05, 2),
                    "arrival_quantity": float(r.arrival_quantity) if r.arrival_quantity is not None else 0.0,
                    "unit": comm_obj.unit or "Rs./Quintal"
                }
    except Exception:
        pass

    # Optional filter by district or state
    compare_items = []
    for item in market_latest_map.values():
        if district and district.lower() not in item["district"].lower():
            continue
        if state and state.lower() not in item["state"].lower():
            continue

        compare_items.append(
            PriceCompareItem(
                market_id=item["market_id"],
                market_name=item["market_name"],
                district=item["district"],
                latitude=item["latitude"],
                longitude=item["longitude"],
                latest_date=item["date"],
                latest_modal_price=item["modal_price"],
                min_price=item["min_price"],
                max_price=item["max_price"],
                arrival_quantity=item["arrival_quantity"],
                unit=item["unit"]
            )
        )

    return sorted(compare_items, key=lambda x: x.market_name)

