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
    q = db.query(Market).filter(Market.is_active == True)

    if commodity_id:
        q = q.join(CleanedMarketPrice, CleanedMarketPrice.market_id == Market.id)\
             .filter(CleanedMarketPrice.commodity_id == commodity_id)\
             .group_by(Market.id)
    elif commodity_name:
        comm = db.query(Commodity).filter(
            (Commodity.canonical_name.ilike(f"%{commodity_name}%")) | (Commodity.original_name.ilike(f"%{commodity_name}%"))
        ).first()
        if comm:
            q = q.join(CleanedMarketPrice, CleanedMarketPrice.market_id == Market.id)\
                 .filter(CleanedMarketPrice.commodity_id == comm.id)\
                 .group_by(Market.id)
        else:
            return []
    return q.order_by(Market.canonical_name.asc()).all()

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

    q = db.query(Market).filter(Market.is_active == True)
    if commodity_name:
        comm = db.query(Commodity).filter(
            (Commodity.canonical_name.ilike(f"%{commodity_name}%")) | (Commodity.original_name.ilike(f"%{commodity_name}%"))
        ).first()
        if comm:
            q = q.join(CleanedMarketPrice, CleanedMarketPrice.market_id == Market.id)\
                 .filter(CleanedMarketPrice.commodity_id == comm.id)\
                 .group_by(Market.id)

    active_markets = q.all()
    valid_market_items, missing_coords_count = calculate_market_distances(
        user_lat=latitude,
        user_lon=longitude,
        markets=active_markets
    )

    ranked_markets = sort_markets_by_distance(valid_market_items, limit=limit)

    return ClosestMarketsResponse(
        user_location=UserLocationOut(latitude=latitude, longitude=longitude),
        markets=[ClosestMarketItem(**m) for m in ranked_markets],
        total_markets_considered=len(active_markets),
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
