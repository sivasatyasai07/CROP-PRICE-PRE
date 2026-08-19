from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import List, Optional, Dict, Any, Literal

PriceSourceType = Literal[
    "official_api",
    "official_csv",
    "predicted_model",
    "fallback_last_observed",
    "fallback_rolling_average",
    "unavailable",
    "predicted"
]
DataStatusType = Literal[
    "observed_live",
    "observed_csv",
    "predicted_model",
    "predicted_fallback",
    "fallback_last_observed",
    "unavailable"
]


class LookupTraceStep(BaseModel):
    source: str
    searched: bool = True
    found: bool = False
    status: Optional[str] = None
    reason: Optional[str] = None


class VerifiedForecastRequest(BaseModel):
    commodity: str
    market: str
    selected_date: date
    district: Optional[str] = None
    state: Optional[str] = "Andhra Pradesh"
    force_refresh: bool = Field(default=True)
    request_id: Optional[str] = None


class ForecastRecord(BaseModel):
    date: date
    target_date: Optional[date] = None
    forecast_origin_date: Optional[date] = None
    horizon: Optional[int] = None
    
    modal_price: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    arrival_quantity: Optional[float] = None
    arrival_unit: Optional[str] = "Metric Tonnes"
    price_unit: Optional[str] = "Rs./Quintal"
    
    price_source: str
    data_status: str
    prediction_status: Optional[str] = "active"  # active, superseded_by_newer_forecast, superseded_by_official, expired, unavailable
    prediction_method: Optional[str] = "none"    # official_observation, trained_model, fallback, none
    model_predict_called: bool = False
    prediction_executed: bool = False
    model_error_code: Optional[str] = None
    raw_model_output: Optional[float] = None
    final_prediction: Optional[float] = None
    
    is_observed: bool
    is_predicted: bool
    
    source_label: str
    verification_status: str = "verified"
    
    source_name: Optional[str] = None
    source_record_id: Optional[str] = None
    fetched_at: Optional[datetime] = None
    data_fetched_at: Optional[datetime] = None
    generated_at: Optional[datetime] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    feature_snapshot_id: Optional[str] = None
    previous_forecast: Optional[Dict[str, Any]] = None
    data_freshness: Optional[str] = None
    
    # Uncertainty & Intervals
    confidence_level: Optional[float] = None
    confidence_source: Optional[str] = None      # calibration_metadata, unavailable
    interval_available: bool = False
    interval_method: Optional[str] = None        # conformal_residual, None
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    confidence_interval: Optional[Dict[str, Optional[float]]] = None
    fallback_reason: Optional[str] = None
    
    # Feature tracking
    arrival_features_used: bool = False
    weather_features_used: bool = False
    seasonal_features_used: bool = False
    arrival_missing: Optional[bool] = None
    weather_missing: Optional[bool] = None
    feature_row_date: Optional[str] = None
    
    # Audit & Verification Trace
    api_checked: bool = True
    api_record_found: bool = False
    master_csv_checked: bool = False
    master_csv_record_found: bool = False
    prediction_generated: bool = False
    final_source: str = "unavailable"
    lookup_trace: List[Dict[str, Any]] = Field(default_factory=list)


class DateRangeSummary(BaseModel):
    start: date
    end: date


class VerifiedForecastResponse(BaseModel):
    request_id: str
    commodity: str
    market: str
    district: Optional[str] = None
    state: Optional[str] = "Andhra Pradesh"
    selected_date: date
    forecast_origin_date: Optional[date] = None
    date_range: DateRangeSummary
    fetched_at: datetime
    api_checked: bool
    api_status: str
    sync_performed: bool
    refresh_performed: bool = True
    latest_observed_price: Optional[float] = None
    latest_observed_date: Optional[str] = None
    trend_direction: Optional[str] = "stable"
    percentage_change_3d: Optional[float] = 0.0
    trend_source: Optional[str] = None
    trend_start_date: Optional[str] = None
    trend_end_date: Optional[str] = None
    trend_start_price: Optional[float] = None
    trend_end_price: Optional[float] = None
    official_values_used: Optional[int] = 0
    predicted_values_used: Optional[int] = 0
    records: List[ForecastRecord]
    summary: Dict[str, int]
    warnings: List[str]
    server_date: Optional[date] = None
    future_dates_disabled: bool = True
    selected_date_valid: bool = True
    api_checked_time: Optional[str] = None
    closest_market_status: str = "active"
    model_version: Optional[str] = None
    feature_snapshot_id: Optional[str] = None
    feature_schema_match: Optional[bool] = True
    missing_features: Optional[List[str]] = Field(default_factory=list)
    unexpected_features: Optional[List[str]] = Field(default_factory=list)
    expected_feature_count: Optional[int] = None
    runtime_feature_count: Optional[int] = None
    feature_explanations: Optional[List[str]] = Field(default_factory=list)
    
    # Live API verification & data freshness
    api_refresh_performed: bool = True
    api_latest_available_date: Optional[date] = None
    database_latest_date: Optional[date] = None
    feature_latest_date: Optional[date] = None
    latest_official_api_date: Optional[date] = None
    latest_stored_official_date: Optional[date] = None
    latest_price_used_for_features: Optional[float] = None
    latest_arrival_used_for_features: Optional[float] = None
    data_refresh_status: Optional[str] = "success"
    data_age_days: Optional[int] = 0
    stale_data_warning: Optional[str] = None
    records_fetched_count: Optional[int] = 0
    records_used_in_features: Optional[int] = 0
    
    # Prediction Service Status & Error Handling
    prediction_service_status: Optional[str] = "success"
    prediction_error_code: Optional[str] = None
    prediction_error_message: Optional[str] = None


class ForecastHistoryItem(BaseModel):
    id: int
    commodity: str
    market: str
    forecast_origin_date: date
    target_date: date
    horizon: int
    predicted_modal_price: float
    lower_bound: float
    upper_bound: float
    price_source: str
    prediction_status: str
    model_version: Optional[str] = None
    feature_snapshot_id: Optional[str] = None
    generated_at: Optional[datetime] = None
    superseded_by_official: bool = False


class OfficialStatusResponse(BaseModel):
    commodity: str
    market: str
    target_date: date
    official_api_checked: bool
    official_record_found: bool
    master_data_checked: bool
    master_record_found: bool
    active_prediction_exists: bool
    final_source: str
    observed_price: Optional[float] = None
