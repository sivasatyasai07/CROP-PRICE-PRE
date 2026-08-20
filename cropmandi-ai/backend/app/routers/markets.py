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
