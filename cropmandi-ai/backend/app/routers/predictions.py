from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.schemas.prediction import PredictionResponse, GeneratePredictionRequest
from app.ml.predict import generate_3day_prediction
from app.models import ModelRun

router = APIRouter(prefix="/api/v1/predictions", tags=["Predictions"])

@router.get("/3-day", response_model=PredictionResponse)
def get_3day_prediction(
    commodity: str = Query(...),
    market: str = Query(...),
    prediction_date: str = Query(None),
    db: Session = Depends(get_db)
):
    if prediction_date is None:
        prediction_date = datetime.now().strftime("%Y-%m-%d")

    active_run = db.query(ModelRun).filter(ModelRun.is_active == True).order_by(ModelRun.created_at.desc()).first()
    version = active_run.model_version if active_run else "1.0.0"

    res = generate_3day_prediction(db, commodity, market, prediction_date, version)
    return res

@router.post("/generate", response_model=PredictionResponse)
def generate_prediction_endpoint(req: GeneratePredictionRequest, db: Session = Depends(get_db)):
    active_run = db.query(ModelRun).filter(ModelRun.is_active == True).order_by(ModelRun.created_at.desc()).first()
    version = active_run.model_version if active_run else "1.0.0"

    date_str = req.prediction_date or datetime.now().strftime("%Y-%m-%d")
    res = generate_3day_prediction(db, req.commodity, req.market, date_str, version)
    return res
