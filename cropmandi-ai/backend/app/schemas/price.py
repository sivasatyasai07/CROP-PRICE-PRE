from pydantic import BaseModel
from typing import Optional, List, Any, Union
from datetime import date


class LatestPriceOut(BaseModel):
    market_id: int
    market_name: str
    district: str
    commodity_id: int
    commodity_name: str
    observation_date: Union[date, str]
    modal_price: float
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    arrival_quantity: Optional[float] = None
    unit: str

    class Config:
        from_attributes = True


class PriceHistoryItem(BaseModel):
    observation_date: Union[date, str]
    modal_price: float
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    arrival_quantity: Optional[float] = None
    quality_status: str


class TrendPointOut(BaseModel):
    date: str
    modal_price: float
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    arrival_quantity: Optional[float] = None
    unit: Optional[str] = "Rs./Quintal"
    price_source: str
    is_observed: bool = True
    is_predicted: bool = False
    data_age_days: int = 0
    source_label: str
    observed_at: str


class CompareMarketOut(BaseModel):
    market: str
    district: str
    state: str
    modal_price: float
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    arrival_quantity: Optional[float] = None
    observation_date: str
    data_age_days: int
    price_source: str
    is_observed: bool = True
    is_predicted: bool = False
    source_label: str
    is_latest_available_value: bool = True
    unit: Optional[str] = "Rs./Quintal"
    market_id: Optional[int] = None


class ExcludedMarketOut(BaseModel):
    market: str
    reason: str
    latest_observation_date: Optional[str] = None
    data_age_days: Optional[int] = None


class CompareResponseOut(BaseModel):
    commodity: str
    requested_date: Optional[str] = None
    current_date: str
    max_latest_value_age_days: int
    markets: List[CompareMarketOut]
    excluded_markets: List[ExcludedMarketOut] = []


class PriceCompareItem(BaseModel):
    market_id: int
    market_name: str
    district: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    latest_date: Union[date, str]
    latest_modal_price: float
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    arrival_quantity: Optional[float] = None
    unit: str


class RecentCommodityOut(BaseModel):
    id: Optional[int] = None
    canonical_name: str
    commodity_name: str
    latest_official_observed_date: Optional[str] = None
    record_count: int
    availability_status: str
    data_age_days: Optional[int] = None


class RecentMarketOut(BaseModel):
    id: Optional[int] = None
    canonical_name: str
    market_name: str
    district: str
    state: str
    latest_official_observed_date: Optional[str] = None
    record_count: int
    availability_status: str
    data_age_days: Optional[int] = None

