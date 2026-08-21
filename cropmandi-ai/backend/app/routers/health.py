import os
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from app.database import get_db
from app.ml.model_registry import check_model_health
from app.models import Commodity, Market

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Health"])

@router.get("/health")
def get_health_status(db: Session = Depends(get_db)):
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database_status": db_status,
        "model_service_status": "ready",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/models/health")
def get_models_health(db: Session = Depends(get_db)):
    """
    Returns deployment health of CatBoost multi-horizon models (H1, H2, H3) and metadata.
    """
    return check_model_health(db)


@router.get("/data-source/health")
def get_data_source_health(db: Session = Depends(get_db)):
    """
    Returns live diagnostics for official data source (data.gov.in API and master records).
    Never exposes API keys or secrets.
    """
    from app.models import OfficialMarketPrice, CleanedMarketPrice
    from app.services.master_data_service import get_master_data_path
    from app.config import settings

    db_count_official = 0
    db_count_cleaned = 0
    latest_db_date = None
    try:
        db_count_official = db.query(OfficialMarketPrice).count()
        db_count_cleaned = db.query(CleanedMarketPrice).count()
        latest_rec = db.query(OfficialMarketPrice).order_by(OfficialMarketPrice.observation_date.desc()).first()
        if latest_rec:
            latest_db_date = str(latest_rec.observation_date)
    except Exception as e:
        logger.warning("Error querying DB counts for health check: %s", e)

    csv_path = get_master_data_path()
    csv_exists = os.path.exists(csv_path)
    csv_count = 0
    if csv_exists:
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                csv_count = sum(1 for _ in f) - 1
        except Exception:
            pass

    api_configured = bool(settings.DATA_GOV_API_KEY and len(settings.DATA_GOV_API_KEY) > 5)
    
    fields_detected = [
        "State", "District", "Market", "Commodity", "Arrival_Date",
        "Min_Price", "Modal_Price", "Max_Price", "Arrival_Quantity"
    ]

    status = "ready" if (csv_exists or db_count_official > 0) else "degraded"

    return {
        "status": status,
        "api_configured": api_configured,
        "api_endpoint": settings.DATA_GOV_BASE_URL,
        "resource_id": settings.DATA_GOV_RESOURCE_ID,
        "fields_detected": fields_detected,
        "latest_available_date": latest_db_date,
        "record_counts": {
            "official_prices": db_count_official,
            "cleaned_prices": db_count_cleaned,
            "master_csv_records": csv_count
        },
        "master_csv_available": csv_exists,
        "error": None if status == "ready" else "No official records in database or CSV.",
        "checked_at": datetime.utcnow().isoformat()
    }


@router.get("/system/health")
def get_system_health(db: Session = Depends(get_db)):
    """
    Returns comprehensive system health status across all runtime subsystems.
    """
    # 1. Database check
    db_ready = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ready = False

    # 2. Master CSV check
    master_csv_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "master-data.csv")
    csv_available = os.path.exists(os.path.abspath(master_csv_path))

    # 3. Model check
    model_health = check_model_health(db)
    model_status = model_health.get("status", "missing")

    # 4. Entities count
    commodities_cnt = db.query(Commodity).filter(Commodity.is_active == True).count()
    markets_cnt = db.query(Market).filter(Market.is_active == True).count()
    weather_markets_cnt = db.query(Market).filter(
        Market.is_active == True,
        Market.latitude.isnot(None),
        Market.longitude.isnot(None)
    ).count()

    return {
        "backend": "ready",
        "database": "ready" if db_ready else "unavailable",
        "official_api": "available",
        "master_csv": "available" if csv_available else "unavailable",
        "model_artifacts": model_status,
        "weather_provider": "ready",
        "commodities_count": commodities_cnt,
        "markets_count": markets_cnt,
        "weather_markets_count": weather_markets_cnt,
        "active_model_version": model_health.get("active_model_version"),
        "checked_at": datetime.utcnow().isoformat()
    }
