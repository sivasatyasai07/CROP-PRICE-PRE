import sys
import os
from datetime import date

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import SessionLocal
from app.models import Market
from app.services.weather_service import sync_market_weather

def main():
    print("Syncing Open-Meteo weather data for all active markets...")
    db = SessionLocal()
    try:
        markets = db.query(Market).filter(Market.is_active == True).all()
        total_synced = 0
        start_d = date(2023, 1, 1)
        end_d = date(2026, 8, 16)
        
        for m in markets:
            if m.latitude and m.longitude:
                count = sync_market_weather(db, m.id, start_d, end_d)
                print(f"Synced {count} weather observations for {m.canonical_name}")
                total_synced += count

        print(f"Weather sync complete! Total observations synced: {total_synced}")
    except Exception as e:
        print(f"Error syncing weather: {str(e)}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
