import argparse
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import SessionLocal
from app.ml.predict import generate_3day_prediction

def main():
    parser = argparse.ArgumentParser(description="Generate 3-Day Mandi Price Prediction")
    parser.add_argument("--commodity", type=str, default="Tomato")
    parser.add_argument("--market", type=str, default="Kalikiri APMC")
    parser.add_argument("--prediction-date", type=str, default="2026-08-13")
    args = parser.parse_args()

    print(f"Generating 3-day forecast for '{args.commodity}' at '{args.market}' on {args.prediction_date}...")
    db = SessionLocal()
    try:
        res = generate_3day_prediction(db, args.commodity, args.market, args.prediction_date)
        print("\n" + json.dumps(res, indent=2))
    except Exception as e:
        print(f"Prediction failed: {str(e)}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
