from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.services.recommendation_service import recommend_best_markets

router = APIRouter(prefix="/api/v1/recommendations", tags=["Recommendations"])

@router.get("/best-market")
def get_best_market_recommendation(
    commodity: str = Query(...),
    prediction_date: str = Query("2026-08-13"),
    farmer_location_lat: Optional[float] = Query(None),
    farmer_location_lon: Optional[float] = Query(None),
    crop_quantity_qtl: Optional[float] = Query(None),
    transport_cost_per_km: Optional[float] = Query(None),
    commission_pct: Optional[float] = Query(0.0),
    wastage_pct: Optional[float] = Query(0.0),
    db: Session = Depends(get_db)
):
    return recommend_best_markets(
        db, commodity, prediction_date,
        farmer_lat=farmer_location_lat,
        farmer_lon=farmer_location_lon,
        crop_quantity_qtl=crop_quantity_qtl,
        transport_cost_per_km=transport_cost_per_km,
        commission_pct=commission_pct,
        wastage_pct=wastage_pct
    )
