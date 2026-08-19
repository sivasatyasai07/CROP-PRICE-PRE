from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date

class TrainModelRequest(BaseModel):
    commodities: List[str] = ["Tomato"]
    markets: List[str] = ["Madanapalli APMC", "Kalikiri APMC", "B.Kothakota H/Q Angallu", "Anantapur APMC"]
    train_start: str = "2021-01-01"
    train_end: str = "2025-12-31"
    validation_start: str = "2025-07-01"
    validation_end: str = "2025-12-31"
    test_start: str = "2026-01-01"
    test_end: str = "2026-12-31"
    model_type: str = "catboost"
    target: str = "modal_price"

class ModelRunOut(BaseModel):
    id: int
    model_name: str
    model_version: str
    training_start_date: Optional[date] = None
    training_end_date: Optional[date] = None
    test_start_date: Optional[date] = None
    test_end_date: Optional[date] = None
    training_rows: int
    metrics_json: Optional[Dict[str, Any]] = None
    status: str
    is_active: bool

    class Config:
        from_attributes = True
