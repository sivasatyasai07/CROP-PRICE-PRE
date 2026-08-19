from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Commodity, CleanedMarketPrice
from app.schemas.commodity import CommodityOut
from sqlalchemy import func

from datetime import date, timedelta

router = APIRouter(prefix="/api/v1/commodities", tags=["Commodities"])

@router.get("", response_model=List[CommodityOut])
def list_commodities(db: Session = Depends(get_db)):
    max_obs_date = db.query(func.max(CleanedMarketPrice.observation_date)).scalar() or date.today()
    cutoff_date = max_obs_date - timedelta(days=20)

    return db.query(Commodity)\
             .join(CleanedMarketPrice, CleanedMarketPrice.commodity_id == Commodity.id)\
             .filter(Commodity.is_active == True)\
             .group_by(Commodity.id)\
             .having(func.max(CleanedMarketPrice.observation_date) >= cutoff_date)\
             .all()
