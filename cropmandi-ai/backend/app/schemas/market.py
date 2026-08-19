from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MarketBase(BaseModel):
    canonical_name: str
    original_name: str
    district: str
    state: str = "Andhra Pradesh"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class MarketOut(MarketBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class MarketDetail(MarketOut):
    commodities: List[str] = []

class UserLocationOut(BaseModel):
    latitude: float
    longitude: float

class ClosestMarketItem(BaseModel):
    market_id: int
    market_name: str
    district: str
    state: str = "Andhra Pradesh"
    latitude: float
    longitude: float
    distance_km: float
    rank: int

class ClosestMarketsResponse(BaseModel):
    user_location: UserLocationOut
    markets: List[ClosestMarketItem]
    total_markets_considered: int
    markets_without_coordinates: int
