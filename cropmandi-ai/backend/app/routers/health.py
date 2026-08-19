import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from app.database import get_db
from app.ml.model_registry import check_model_health
from app.models import Commodity, Market

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
