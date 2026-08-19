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
    commodities = db.query(Commodity).filter(Commodity.is_active == True).order_by(Commodity.canonical_name.asc()).all()
    if not commodities:
        from app.services.seed_service import seed_markets_and_commodities
        seed_markets_and_commodities(db)
        commodities = db.query(Commodity).filter(Commodity.is_active == True).order_by(Commodity.canonical_name.asc()).all()
    return commodities
