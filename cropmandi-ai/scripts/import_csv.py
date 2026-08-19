import argparse
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import SessionLocal, engine, Base
import app.models # Ensure models are loaded

Base.metadata.create_all(bind=engine)
from app.services.csv_ingestion_service import ingest_csv_data

def main():
    parser = argparse.ArgumentParser(description="Import CSV dataset into CropMandi AI raw_market_prices table")
    parser.add_argument("--file", type=str, required=True, help="Path to CSV file")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' does not exist.")
        sys.exit(1)

    print(f"Importing raw dataset from '{args.file}'...")
    db = SessionLocal()
    try:
        records = ingest_csv_data(args.file, db)
        print(f"Successfully imported {len(records)} raw records into database.")
    except Exception as e:
        print(f"Failed to import CSV: {str(e)}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
