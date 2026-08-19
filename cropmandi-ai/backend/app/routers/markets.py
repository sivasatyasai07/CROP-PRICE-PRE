from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta
from sqlalchemy import func

from app.database import get_db
from app.models import Market, CleanedMarketPrice, Commodity
from app.schemas.market import MarketOut, MarketDetail, ClosestMarketsResponse, ClosestMarketItem, UserLocationOut
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
            from app.services.master_data_service import get_master_data_path
            import os
            import pandas as pd

            norm_target_c = normalize_commodity_name(target_comm_name).lower()
            matched_market_names = set()

            # 1. From DB
            if commodity_id:
                db_m_ids = db.query(CleanedMarketPrice.market_id).filter(
                    CleanedMarketPrice.commodity_id == commodity_id
                ).distinct().all()
                for m_id_tuple in db_m_ids:
                    m = db.query(Market).filter(Market.id == m_id_tuple[0]).first()
                    if m:
                        matched_market_names.add(normalize_market_name(m.canonical_name).lower())

            # 2. From master-data.csv
            csv_path = get_master_data_path()
            if os.path.exists(csv_path):
                try:
                    df = pd.read_csv(csv_path)
                    comm_col = [col for col in df.columns if 'commodity' in col.lower() and 'group' not in col.lower()][0]
                    mkt_col = [col for col in df.columns if 'market' in col.lower()][0]
                    sub = df[df[comm_col].astype(str).apply(normalize_commodity_name).str.lower() == norm_target_c]
                    for m_name in sub[mkt_col].dropna().unique():
                        matched_market_names.add(normalize_market_name(str(m_name)).lower())
                except Exception:
                    pass

            if matched_market_names:
                filtered_markets = [
                    m for m in all_markets
                    if normalize_market_name(m.canonical_name).lower() in matched_market_names or
                       normalize_market_name(m.original_name or "").lower() in matched_market_names
                ]
                if filtered_markets:
                    return filtered_markets

    return all_markets

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
