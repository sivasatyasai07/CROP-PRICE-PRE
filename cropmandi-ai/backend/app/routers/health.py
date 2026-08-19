from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from app.database import get_db

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
