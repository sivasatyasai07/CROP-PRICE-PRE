from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta
from sqlalchemy import func

from app.database import get_db
from app.models import Market, CleanedMarketPrice, Commodity
from app.schemas.market import MarketOut, MarketDetail, ClosestMarketsResponse, ClosestMarketItem, UserLocationOut
from app.schemas.price import RecentMarketOut
from app.utils.geolocation import validate_coordinates, calculate_market_distances, sort_markets_by_distance

router = APIRouter(prefix="/api/v1/markets", tags=["Markets"])

@router.get("", response_model=List[MarketOut])
def list_markets(
    commodity_id: Optional[int] = None,
    commodity_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    all_markets = db.query(Market).filter(Market.is_active == True).order_by(Market.canonical_name.asc()).all()
    if not all_markets:
        from app.services.seed_service import seed_markets_and_commodities
        seed_markets_and_commodities(db)
        all_markets = db.query(Market).filter(Market.is_active == True).order_by(Market.canonical_name.asc()).all()

    if commodity_id is not None or commodity_name is not None:
        target_comm_name = None
        if commodity_id is not None:
            c = db.query(Commodity).filter(Commodity.id == commodity_id).first()
            if c:
                target_comm_name = c.canonical_name
        elif commodity_name:
            target_comm_name = commodity_name

        if target_comm_name:
            from app.utils.market_normalization import normalize_commodity_name, normalize_market_name
            from app.services.master_data_service import load_master_data
            
            norm_target_c = normalize_commodity_name(target_comm_name).lower()
            master_idx = load_master_data()

            matched_market_norms = set()
            for (c, m, d) in master_idx.keys():
                if c == norm_target_c:
                    matched_market_norms.add(m)

            if matched_market_norms:
                filtered_markets = [
                    m for m in all_markets
                    if normalize_market_name(m.canonical_name).lower() in matched_market_norms or
                       normalize_market_name(m.original_name or "").lower() in matched_market_norms
                ]
                if filtered_markets:
                    return filtered_markets

@router.get("/recent", response_model=List[RecentMarketOut])
def list_recent_markets(
    commodity: Optional[str] = Query(None),
    commodity_id: Optional[int] = Query(None),
    days: int = Query(30, ge=1, le=365),
    min_records: int = Query(3, ge=1),
    db: Session = Depends(get_db)
):
    from app.schemas.price import RecentMarketOut
    from app.utils.date_service import get_ist_today
    from app.utils.market_normalization import normalize_commodity_name, normalize_market_name
    from app.services.master_data_service import load_master_data
    from app.models import OfficialMarketPrice
    from datetime import datetime

    if not isinstance(commodity_id, int):
        commodity_id = None
    if not isinstance(commodity, str):
        commodity = None
    if not isinstance(days, int) or days <= 0:
        days = 30
    if not isinstance(min_records, int) or min_records <= 0:
        min_records = 3

    today = get_ist_today()
    start_date = today - timedelta(days=days - 1)

    target_comm_name = None
    if commodity_id is not None:
        c_obj = db.query(Commodity).filter(Commodity.id == commodity_id).first()
        if c_obj:
            target_comm_name = c_obj.canonical_name
    elif commodity:
        target_comm_name = commodity

    norm_target_c = normalize_commodity_name(target_comm_name).lower() if target_comm_name else None
    start_date_str = start_date.strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")

    all_markets = db.query(Market).filter(Market.is_active == True).order_by(Market.canonical_name.asc()).all()
    if not all_markets:
        from app.services.seed_service import seed_markets_and_commodities
        seed_markets_and_commodities(db)
        all_markets = db.query(Market).filter(Market.is_active == True).order_by(Market.canonical_name.asc()).all()

    master_idx = load_master_data()

    # Fast single-pass tally from master data for this commodity
    master_mkt_counts = {}
    master_mkt_latest = {}
    for (comm_key, mkt_key, d_str), rec in master_idx.items():
        if norm_target_c is None or comm_key == norm_target_c:
            if start_date_str <= d_str <= today_str:
                try:
                    p_val = float(rec.get("modal_price", 0))
                    if p_val > 0:
                        master_mkt_counts[mkt_key] = master_mkt_counts.get(mkt_key, 0) + 1
                        if mkt_key not in master_mkt_latest or d_str > master_mkt_latest[mkt_key]:
                            master_mkt_latest[mkt_key] = d_str
                except Exception:
                    pass

    # DB records aggregation
    db_mkt_counts = {}
    db_mkt_latest = {}
    try:
        q = db.query(OfficialMarketPrice).filter(
            OfficialMarketPrice.observation_date >= start_date,
            OfficialMarketPrice.observation_date <= today
        )
        if commodity_id:
            q = q.filter(OfficialMarketPrice.commodity_id == commodity_id)
        elif target_comm_name:
            c_ent = db.query(Commodity).filter(Commodity.canonical_name == target_comm_name).first()
            if c_ent:
                q = q.filter(OfficialMarketPrice.commodity_id == c_ent.id)

        for r in q.all():
            if float(r.modal_price) > 0:
                mid = r.market_id
                db_mkt_counts[mid] = db_mkt_counts.get(mid, 0) + 1
                d_val = r.observation_date if isinstance(r.observation_date, date) else datetime.strptime(str(r.observation_date), "%Y-%m-%d").date()
                if mid not in db_mkt_latest or d_val > db_mkt_latest[mid]:
                    db_mkt_latest[mid] = d_val
    except Exception:
        pass

    results: List[RecentMarketOut] = []

    for m in all_markets:
        norm_m = normalize_market_name(m.canonical_name).lower()
        norm_orig_m = normalize_market_name(m.original_name or "").lower()

        m_cnt = master_mkt_counts.get(norm_m, 0) or master_mkt_counts.get(norm_orig_m, 0)
        records_in_window = m_cnt + db_mkt_counts.get(m.id, 0)

        latest_date_dt = None
        latest_str = master_mkt_latest.get(norm_m) or master_mkt_latest.get(norm_orig_m)
        if latest_str:
            latest_date_dt = datetime.strptime(latest_str, "%Y-%m-%d").date()
        if m.id in db_mkt_latest:
            if latest_date_dt is None or db_mkt_latest[m.id] > latest_date_dt:
                latest_date_dt = db_mkt_latest[m.id]

        if records_in_window >= min_records:
            age_days = (today - latest_date_dt).days if latest_date_dt else None
            status = "available" if records_in_window >= 5 else "limited"
            results.append(RecentMarketOut(
                id=m.id,
                canonical_name=m.canonical_name,
                market_name=m.canonical_name,
                district=m.district,
                state=m.state,
                latest_official_observed_date=latest_date_dt.strftime("%Y-%m-%d") if latest_date_dt else None,
                record_count=records_in_window,
                availability_status=status,
                data_age_days=age_days
            ))

    return sorted(results, key=lambda x: x.record_count, reverse=True)



@router.get("/closest", response_model=ClosestMarketsResponse)
def get_closest_markets(
    latitude: float = Query(..., description="User latitude"),
    longitude: float = Query(..., description="User longitude"),
    commodity_name: Optional[str] = Query(None, description="Optional commodity filter"),
    limit: Optional[int] = Query(None, ge=1, description="Max closest markets to return"),
    db: Session = Depends(get_db)
):
    if not validate_coordinates(latitude, longitude):
        raise HTTPException(
            status_code=400,
            detail="Invalid latitude or longitude coordinates provided."
        )

    markets = db.query(Market).filter(Market.is_active == True).all()
    if len(markets) < 5:
        from app.services.seed_service import seed_markets_and_commodities
        seed_markets_and_commodities(db)
        markets = db.query(Market).filter(Market.is_active == True).all()

    valid_market_items, missing_coords_count = calculate_market_distances(
        user_lat=latitude,
        user_lon=longitude,
        markets=markets
    )

    ranked_markets = sort_markets_by_distance(valid_market_items, limit=limit)

    return ClosestMarketsResponse(
        user_location=UserLocationOut(latitude=latitude, longitude=longitude),
        markets=[ClosestMarketItem(**m) for m in ranked_markets],
        total_markets_considered=len(markets),
        markets_without_coordinates=missing_coords_count
    )

@router.get("/{market_id}", response_model=MarketDetail)
def get_market(market_id: int, db: Session = Depends(get_db)):
    market = db.query(Market).filter(Market.id == market_id).first()
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
        
    commodities = db.query(Commodity.canonical_name)\
                    .join(CleanedMarketPrice, CleanedMarketPrice.commodity_id == Commodity.id)\
                    .filter(CleanedMarketPrice.market_id == market_id)\
                    .distinct().all()
                    
    comm_names = [c[0] for c in commodities]
    
    return MarketDetail(
        id=market.id,
        canonical_name=market.canonical_name,
        original_name=market.original_name,
        district=market.district,
        state=market.state,
        latitude=market.latitude,
        longitude=market.longitude,
        is_active=market.is_active,
        created_at=market.created_at,
        commodities=comm_names
    )

@router.get("/{market_id}/commodities")
def get_market_commodities(market_id: int, db: Session = Depends(get_db)):
    commodities = db.query(Commodity)\
                    .join(CleanedMarketPrice, CleanedMarketPrice.commodity_id == Commodity.id)\
                    .filter(CleanedMarketPrice.market_id == market_id)\
                    .distinct().all()
    return commodities
