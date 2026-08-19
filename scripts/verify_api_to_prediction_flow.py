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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_api_to_prediction_flow")

def main():
    os.makedirs("reports", exist_ok=True)
    db = SessionLocal()
    try:
        seed_markets_and_commodities(db)
        
        req = VerifiedForecastRequest(
            commodity="Tomato",
            market="Madanapalle APMC",
            selected_date=datetime.date(2026, 8, 17),
            include_live_sync=True
        )

        resp = reconcile_verified_forecast(db, req)
        
        record_summaries = []
        for r in resp.records:
            record_summaries.append({
                "target_date": str(r.target_date),
                "horizon": r.horizon,
                "modal_price": r.modal_price,
                "price_source": r.price_source,
                "prediction_method": r.prediction_method,
                "prediction_status": r.prediction_status,
                "interval_available": r.interval_available,
                "is_observed": r.is_observed,
                "is_predicted": r.is_predicted
            })

        flow_report = {
            "commodity": resp.commodity,
            "market": resp.market,
            "selected_date": str(resp.selected_date),
            "latest_observed_price": resp.latest_observed_price,
            "trend_direction": resp.trend_direction,
            "model_version": getattr(resp, "model_version", "v20260818_153724"),
            "records": record_summaries,
            "flow_verified": len(record_summaries) >= 3 and any(r["modal_price"] is not None for r in record_summaries)
        }

        with open("reports/api_to_prediction_verification_report.json", "w") as f:
            json.dump(flow_report, f, indent=2)

        logger.info("API to Prediction Flow Report saved to reports/api_to_prediction_verification_report.json")
        if not flow_report["flow_verified"]:
            sys.exit(1)
        sys.exit(0)
    finally:
        db.close()

if __name__ == "__main__":
    main()
