from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from app.database import get_db
from app.models import ModelRun
from app.schemas.training import TrainModelRequest, ModelRunOut
from app.ml.dataset_builder import build_dataset_from_db, chronological_split
from app.ml.train import train_catboost_models

router = APIRouter(prefix="/api/v1/models", tags=["Training"])

@router.post("/train", response_model=ModelRunOut)
def train_model_endpoint(req: TrainModelRequest, db: Session = Depends(get_db)):
    df_all = build_dataset_from_db(db)
    if df_all.empty:
        raise HTTPException(status_code=400, detail="No cleaned dataset available to train models.")

    train_df, test_df = chronological_split(df_all, train_end=req.train_end, test_start=req.test_start)

    model_version = f"v{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    metadata = train_catboost_models(
        train_df, test_df,
        model_version=model_version
    )

    # Deactivate previous active models
    db.query(ModelRun).update({"is_active": False})

    model_run = ModelRun(
        model_name="CatBoostRegressor Direct 3-Horizon",
        model_version=model_version,
        training_start_date=datetime.strptime(req.train_start, "%Y-%m-%d").date(),
        training_end_date=datetime.strptime(req.train_end, "%Y-%m-%d").date(),
        test_start_date=datetime.strptime(req.test_start, "%Y-%m-%d").date(),
        test_end_date=datetime.strptime(req.test_end, "%Y-%m-%d").date(),
        training_rows=len(train_df),
        metrics_json=metadata.get("metrics"),
        artifact_path=f"ml/models/catboost_h1_v{model_version}.cbm",
        status="completed",
        is_active=True
    )

    db.add(model_run)
    db.commit()
    db.refresh(model_run)

    return model_run

@router.get("", response_model=List[ModelRunOut])
def list_model_runs(db: Session = Depends(get_db)):
    return db.query(ModelRun).order_by(ModelRun.created_at.desc()).all()

@router.get("/{model_run_id}", response_model=ModelRunOut)
def get_model_run(model_run_id: int, db: Session = Depends(get_db)):
    run = db.query(ModelRun).get(model_run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Model run not found")
    return run
