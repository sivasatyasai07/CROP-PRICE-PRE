from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class GeneratePredictionRequest(BaseModel):
    commodity: str
    market: str
    prediction_date: Optional[str] = "2026-08-13"

class PredictionHorizonOut(BaseModel):
    target_date: str
    horizon: int
    predicted_modal_price: float
    lower_bound: float
    upper_bound: float
    confidence_level: float = 0.80
    is_actual: bool = False

class PredictionResponse(BaseModel):
    commodity: str
    market: str
    unit: str
    prediction_date: str
    latest_observed_price: float
    latest_observed_date: str
    trend_direction: str  # upward, downward, stable
    percentage_change_3d: float
    predictions: List[PredictionHorizonOut]
    warning: str = "Prices can change because of arrivals, quality, demand, weather, transport, festivals, and local market conditions. Use this prediction as decision support, not as a guaranteed selling price."
    model_name: str = "CatBoostRegressor v1.0"
    model_version: str = "1.0.0"
    data_freshness: str = "Current"
    weather_available: bool = True
    fallback_used: bool = False
    fallback_reason: Optional[str] = None
