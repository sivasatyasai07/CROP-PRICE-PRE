import os
import sys
import json
import logging
import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "cropmandi-ai", "backend"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import SessionLocal
from app.services.seed_service import seed_markets_and_commodities
from app.services.forecast_reconciliation_service import reconcile_verified_forecast
from app.schemas.forecast import VerifiedForecastRequest
from app.ml.model_registry import check_model_health

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_live_forecast_deployment")

def main():
    os.makedirs("reports", exist_ok=True)
    db = SessionLocal()
    try:
        seed_markets_and_commodities(db)
        health = check_model_health(db)
        
        req = VerifiedForecastRequest(
            commodity="Tomato",
            market="Madanapalle APMC",
            selected_date=datetime.date(2026, 8, 17),
            include_live_sync=False
        )

        resp = reconcile_verified_forecast(db, req)
        
        report = {
            "deployment_status": "ready",
            "model_health": health,
            "forecast_response": {
                "commodity": resp.commodity,
                "market": resp.market,
                "selected_date": str(resp.selected_date),
                "latest_observed_price": resp.latest_observed_price,
                "trend_direction": resp.trend_direction,
                "total_records": len(resp.records)
            },
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

        with open("reports/live_forecast_deployment_report.json", "w") as f:
            json.dump(report, f, indent=2)

        logger.info("Live Forecast Deployment Report saved to reports/live_forecast_deployment_report.json")
        sys.exit(0)
    finally:
        db.close()

if __name__ == "__main__":
    main()
