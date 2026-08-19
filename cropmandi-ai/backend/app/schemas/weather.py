from pydantic import BaseModel
from typing import Optional
from datetime import date

class WeatherSyncRequest(BaseModel):
    market_id: int
    start_date: str
    end_date: str

class WeatherOut(BaseModel):
    market_id: int
    observation_date: date
    temperature_max: Optional[float] = None
    temperature_min: Optional[float] = None
    precipitation: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    weather_code: Optional[int] = None
    is_historical: bool

    class Config:
        from_attributes = True
