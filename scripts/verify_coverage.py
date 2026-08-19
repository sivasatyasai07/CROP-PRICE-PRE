import os
import sys
import json
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "cropmandi-ai", "backend"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import SessionLocal
from app.models import Commodity, Market, CleanedMarketPrice
from app.services.seed_service import seed_markets_and_commodities

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_coverage")

def main():
    os.makedirs("reports", exist_ok=True)
    db = SessionLocal()
    try:
        seed_markets_and_commodities(db)
        commodities = db.query(Commodity).filter(Commodity.is_active == True).all()
        markets = db.query(Market).filter(Market.is_active == True).all()
        coords_markets = [m for m in markets if m.latitude is not None and m.longitude is not None]

        report = {
            "commodities_count": len(commodities),
            "commodities": [c.canonical_name for c in commodities],
            "markets_count": len(markets),
            "markets_with_coordinates": len(coords_markets),
            "markets": [{"id": m.id, "name": m.canonical_name, "district": m.district, "coords": [m.latitude, m.longitude]} for m in markets],
            "status": "success" if len(commodities) >= 15 and len(markets) >= 20 else "insufficient_coverage"
        }

        with open("reports/coverage_report.json", "w") as f:
            json.dump(report, f, indent=2)

        logger.info("Coverage Report saved to reports/coverage_report.json: %d commodities, %d markets", len(commodities), len(markets))
        if report["status"] != "success":
            sys.exit(1)
        sys.exit(0)
    finally:
        db.close()

if __name__ == "__main__":
    main()
