import sys
import os
import argparse
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import SessionLocal
from app.services.official_market_sync_service import sync_latest_market_data

def main():
    parser = argparse.ArgumentParser(description="Synchronize latest rolling window mandi price data")
    parser.add_argument("--lookback-days", type=int, default=7)
    args = parser.parse_args()

    db = SessionLocal()
    try:
        print(f"Starting latest mandi price synchronization (lookback={args.lookback_days} days)...")
        report = sync_latest_market_data(db=db, lookback_days=args.lookback_days)
        print("Synchronization finished:")
        print(json.dumps(report, indent=2, default=str))
    finally:
        db.close()

if __name__ == "__main__":
    main()
