from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import List
from app.database import get_db
from app.models import WeatherObservation, Market
from app.schemas.weather import WeatherOut, WeatherSyncRequest
from app.services.weather_service import sync_market_weather

router = APIRouter(prefix="/api/v1/weather", tags=["Weather"])

@router.post("/sync")
def sync_weather(req: WeatherSyncRequest, db: Session = Depends(get_db)):
    start_dt = datetime.strptime(req.start_date, "%Y-%m-%d").date()
    end_dt = datetime.strptime(req.end_date, "%Y-%m-%d").date()

    count = sync_market_weather(db, req.market_id, start_dt, end_dt)
    return {"status": "success", "market_id": req.market_id, "saved_observations": count}

@router.get("/history", response_model=List[WeatherOut])
def get_weather_history(market_id: int = Query(...), db: Session = Depends(get_db)):
    obs = db.query(WeatherObservation)\
            .filter(WeatherObservation.market_id == market_id, WeatherObservation.is_historical == True)\
            .order_by(WeatherObservation.observation_date.desc()).limit(30).all()
    
    # Auto-fetch if not yet in database
    if not obs:
        today = date.today()
        sync_market_weather(db, market_id, today - timedelta(days=14), today)
        obs = db.query(WeatherObservation)\
                .filter(WeatherObservation.market_id == market_id, WeatherObservation.is_historical == True)\
                .order_by(WeatherObservation.observation_date.desc()).limit(30).all()
    return obs

@router.get("/forecast", response_model=List[WeatherOut])
def get_weather_forecast(market_id: int = Query(...), db: Session = Depends(get_db)):
    obs = db.query(WeatherObservation)\
            .filter(WeatherObservation.market_id == market_id, WeatherObservation.is_historical == False)\
            .order_by(WeatherObservation.observation_date.asc()).limit(7).all()
    
    # Auto-fetch if not yet in database
    if not obs:
        today = date.today()
        sync_market_weather(db, market_id, today, today + timedelta(days=7))
        obs = db.query(WeatherObservation)\
                .filter(WeatherObservation.market_id == market_id, WeatherObservation.is_historical == False)\
                .order_by(WeatherObservation.observation_date.asc()).limit(7).all()
    return obs
