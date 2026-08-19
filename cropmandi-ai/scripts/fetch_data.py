import argparse
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import SessionLocal
from app.services.data_gov_service import fetch_data_gov_prices

def main():
    parser = argparse.ArgumentParser(description="Fetch official market data from data.gov.in")
    parser.add_argument("--state", type=str, default="Andhra Pradesh", help="State name to filter by")
    parser.add_argument("--limit", type=int, default=1000, help="Number of records to fetch")
    parser.add_argument("--start-date", type=str, default="2021-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, default="2026-12-31", help="End date (YYYY-MM-DD)")
    args = parser.parse_args()

    print(f"Fetching official data for state='{args.state}', limit={args.limit} from data.gov.in...")
    db = SessionLocal()
    try:
        recs = fetch_data_gov_prices(db, state=args.state, limit=args.limit)
        print(f"Successfully fetched and stored {len(recs)} raw records into database.")
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
