from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import CleanedMarketPrice, RawMarketPrice, ModelRun, WeatherObservation, DataQualityReport
from sqlalchemy import func

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])

@router.get("/status")
def get_admin_status(db: Session = Depends(get_db)):
    last_ingestion = db.query(func.max(RawMarketPrice.imported_at)).scalar()
    last_cleaning = db.query(func.max(CleanedMarketPrice.created_at)).scalar()
    last_weather = db.query(func.max(WeatherObservation.created_at)).scalar()
    last_training = db.query(func.max(ModelRun.created_at)).scalar()
    
    active_model = db.query(ModelRun).filter(ModelRun.is_active == True).first()
    
    total_raw = db.query(RawMarketPrice).count()
    total_cleaned = db.query(CleanedMarketPrice).count()

    return {
        "last_successful_ingestion": last_ingestion.isoformat() if last_ingestion else None,
        "last_successful_cleaning": last_cleaning.isoformat() if last_cleaning else None,
        "last_successful_weather_sync": last_weather.isoformat() if last_weather else None,
        "last_successful_training": last_training.isoformat() if last_training else None,
        "active_model_version": active_model.model_version if active_model else "None",
        "total_raw_records": total_raw,
        "total_cleaned_records": total_cleaned,
        "status": "operational"
    }
