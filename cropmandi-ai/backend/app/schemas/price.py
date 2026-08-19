from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class LatestPriceOut(BaseModel):
    market_id: int
    market_name: str
    district: str
    commodity_id: int
    commodity_name: str
    observation_date: date
    modal_price: float
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    arrival_quantity: Optional[float] = None
    unit: str

    class Config:
        from_attributes = True

class PriceHistoryItem(BaseModel):
    observation_date: date
    modal_price: float
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    arrival_quantity: Optional[float] = None
    quality_status: str

class PriceCompareItem(BaseModel):
    market_id: int
    market_name: str
    district: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    latest_date: date
    latest_modal_price: float
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    arrival_quantity: Optional[float] = None
    unit: str
