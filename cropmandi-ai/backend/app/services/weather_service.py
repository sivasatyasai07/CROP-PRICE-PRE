import httpx
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from app.config import settings
from app.models import Market, WeatherObservation
from typing import List, Dict, Any, Optional

class OpenMeteoWeatherProvider:
    def __init__(self):
        self.forecast_url = settings.WEATHER_API_URL
        self.archive_url = settings.WEATHER_HISTORICAL_API_URL

    def fetch_weather(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        today = date(2026, 8, 13)
        results = []

        # If range includes historical dates (<= today - 2 days)
        if start_date <= today:
            archive_end = min(end_date, today)
            try:
                params = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "start_date": str(start_date),
                    "end_date": str(archive_end),
                    "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "relative_humidity_2m_mean", "wind_speed_10m_max", "weather_code"],
                    "timezone": "Asia/Kolkata"
                }
                resp = httpx.get(f"{self.archive_url}/archive", params=params, timeout=15.0)
                if resp.status_code == 200:
                    d = resp.json().get("daily", {})
                    dates = d.get("time", [])
                    t_max = d.get("temperature_2m_max", [])
                    t_min = d.get("temperature_2m_min", [])
                    precip = d.get("precipitation_sum", [])
                    rh = d.get("relative_humidity_2m_mean", [])
                    ws = d.get("wind_speed_10m_max", [])
                    wc = d.get("weather_code", [])

                    for i, dt_str in enumerate(dates):
                        results.append({
                            "date": datetime.strptime(dt_str, "%Y-%m-%d").date(),
                            "temp_max": t_max[i] if i < len(t_max) else 30.0,
                            "temp_min": t_min[i] if i < len(t_min) else 20.0,
                            "precip": precip[i] if i < len(precip) else 0.0,
                            "humidity": rh[i] if i < len(rh) else 60.0,
                            "wind_speed": ws[i] if i < len(ws) else 10.0,
                            "weather_code": wc[i] if i < len(wc) else 0,
                            "is_historical": True
                        })
            except Exception:
                pass # Use fallback if Open-Meteo archive call fails

        # Forecast for future dates
        if end_date > today:
            try:
                params = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "relative_humidity_2m_mean", "wind_speed_10m_max", "weather_code"],
                    "timezone": "Asia/Kolkata"
                }
                resp = httpx.get(f"{self.forecast_url}/forecast", params=params, timeout=10.0)
                if resp.status_code == 200:
                    d = resp.json().get("daily", {})
                    dates = d.get("time", [])
                    t_max = d.get("temperature_2m_max", [])
                    t_min = d.get("temperature_2m_min", [])
                    precip = d.get("precipitation_sum", [])
                    rh = d.get("relative_humidity_2m_mean", [])
                    ws = d.get("wind_speed_10m_max", [])
                    wc = d.get("weather_code", [])

                    for i, dt_str in enumerate(dates):
                        dt_val = datetime.strptime(dt_str, "%Y-%m-%d").date()
                        if dt_val > today and dt_val <= end_date:
                            results.append({
                                "date": dt_val,
                                "temp_max": t_max[i] if i < len(t_max) else 32.0,
                                "temp_min": t_min[i] if i < len(t_min) else 22.0,
                                "precip": precip[i] if i < len(precip) else 0.0,
                                "humidity": rh[i] if i < len(rh) else 65.0,
                                "wind_speed": ws[i] if i < len(ws) else 12.0,
                                "weather_code": wc[i] if i < len(wc) else 0,
                                "is_historical": False
                            })
            except Exception:
                pass

        return results

weather_provider = OpenMeteoWeatherProvider()

def sync_market_weather(db: Session, market_id: int, start_date: date, end_date: date) -> int:
    market = db.query(Market).filter(Market.id == market_id).first()
    if not market or not market.latitude or not market.longitude:
        return 0

    records = weather_provider.fetch_weather(market.latitude, market.longitude, start_date, end_date)
    saved_count = 0

    for rec in records:
        # Check cache
        existing = db.query(WeatherObservation).filter(
            WeatherObservation.market_id == market_id,
            WeatherObservation.observation_date == rec["date"]
        ).first()

        if not existing:
            wx_obj = WeatherObservation(
                market_id=market_id,
                observation_date=rec["date"],
                latitude=market.latitude,
                longitude=market.longitude,
                temperature_max=rec["temp_max"],
                temperature_min=rec["temp_min"],
                precipitation=rec["precip"],
                humidity=rec["humidity"],
                wind_speed=rec["wind_speed"],
                weather_code=rec["weather_code"],
                weather_source="open_meteo",
                is_historical=rec["is_historical"]
            )
            db.add(wx_obj)
            saved_count += 1

    db.commit()
    return saved_count
