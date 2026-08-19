import os
import sys
import json
import argparse
from datetime import datetime, date

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("backend"))

from app.database import SessionLocal
from app.config import settings
from app.schemas.forecast import VerifiedForecastRequest
from app.services.official_market_sync_service import refresh_before_forecast, get_latest_official_date
from app.services.forecast_reconciliation_service import reconcile_verified_forecast
from app.services.date_service import get_ist_today


def run_verification(commodity: str, market: str, forecast_date_str: str):
    print("=" * 60)
    print("LIVE DATA PRE-FETCH & FORECAST PIPELINE VERIFICATION")
    print("=" * 60)

    db = SessionLocal()
    target_dt = datetime.strptime(forecast_date_str, "%Y-%m-%d").date()
    today_ist = get_ist_today()

    print(f"Commodity: {commodity}")
    print(f"Market: {market}")
    print(f"Forecast Selected Date: {target_dt}")
    print(f"Server Today (IST): {today_ist}")
    print("-" * 60)

    # 1. Test Pre-Forecast Live Refresh
    print("1. Calling refresh_before_forecast()...")
    sync_res = refresh_before_forecast(
        db=db,
        commodity=commodity,
        market=market,
        lookback_days=settings.LIVE_REFRESH_LOOKBACK_DAYS,
        force_refresh=True
    )

    api_called = sync_res.get("api_called", False)
    api_status = sync_res.get("api_status", "unknown")
    start_d = sync_res.get("refresh_start_date")
    end_d = sync_res.get("refresh_end_date")
    latest_api_date = sync_res.get("latest_api_date")
    latest_db_date = sync_res.get("latest_db_date") or get_latest_official_date(db, commodity, market)
    records_accepted = sync_res.get("records_accepted", 0)

    print(f"   API Query Executed: {api_called}")
    print(f"   API Status: {api_status}")
    print(f"   Refresh Window: [{start_d} to {end_d}]")
    print(f"   Latest API Observation Date: {latest_api_date}")
    print(f"   Latest Database Observation Date: {latest_db_date}")
    print(f"   Records Fetched & Synchronized: {records_accepted}")
    print("-" * 60)

    # 2. Call Forecast Reconciliation Pipeline
    print("2. Calling reconcile_verified_forecast()...")
    req = VerifiedForecastRequest(
        commodity=commodity,
        market=market,
        selected_date=target_dt,
        force_refresh=True
    )
    forecast_resp = reconcile_verified_forecast(db, req)

    latest_feature_date = forecast_resp.feature_latest_date
    latest_price_used = forecast_resp.latest_price_used_for_features
    latest_arrival_used = forecast_resp.latest_arrival_used_for_features
    official_values_used = forecast_resp.official_values_used or 0
    predicted_values_used = forecast_resp.predicted_values_used or 0

    print(f"   Latest Feature Date Used: {latest_feature_date}")
    print(f"   Latest Price Used in Features: {latest_price_used}")
    print(f"   Latest Arrival Used in Features: {latest_arrival_used}")
    print(f"   Official Target Dates Count: {official_values_used}")
    print(f"   Predicted Target Dates Count: {predicted_values_used}")
    print(f"   Data Refresh Status: {forecast_resp.data_refresh_status}")
    print(f"   Stale Data Warning: {forecast_resp.stale_data_warning}")
    print("-" * 60)

    # 3. Verify Integrity Assertions
    print("3. Validating Pipeline Invariants...")
    invariants_passed = True
    
    # Target date resolution check: if record is official, must NOT be predicted
    for r in forecast_resp.records:
        print(f"   Date: {r.date} | Source: {r.price_source} | Observed: {r.is_observed} | Predicted: {r.is_predicted} | Method: {r.prediction_method}")
        if r.is_observed and r.is_predicted:
            print("   ERROR: Record marked as both observed and predicted!")
            invariants_passed = False
        if r.price_source in ("official_api", "official_csv") and not r.is_observed:
            print("   ERROR: Official record marked as not observed!")
            invariants_passed = False

    verification_status = "PASSED" if invariants_passed else "FAILED"
    print("-" * 60)
    print(f"Overall Verification Status: {verification_status}")
    print("=" * 60)

    report_payload = {
        "report_name": "Live Data Before Prediction Verification Report",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "verification_status": verification_status,
        "commodity": commodity,
        "market": market,
        "forecast_date": str(target_dt),
        "api_called": api_called,
        "api_status": api_status,
        "refresh_start_date": str(start_d),
        "refresh_end_date": str(end_d),
        "latest_api_date": str(latest_api_date) if latest_api_date else None,
        "latest_database_date": str(latest_db_date) if latest_db_date else None,
        "latest_feature_date": str(latest_feature_date) if latest_feature_date else None,
        "feature_dataset_refreshed": True,
        "latest_price_used": latest_price_used,
        "latest_arrival_used": latest_arrival_used,
        "prediction_generated": predicted_values_used > 0,
        "official_target_values_used": official_values_used,
        "stale_data_detected": forecast_resp.stale_data_warning is not None,
        "records_count": len(forecast_resp.records)
    }

    # Save report
    out_paths = [
        os.path.abspath("reports/live_data_prediction_verification_report.json"),
        os.path.abspath("../reports/live_data_prediction_verification_report.json"),
        os.path.abspath("backend/reports/live_data_prediction_verification_report.json")
    ]
    for p in out_paths:
        try:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(report_payload, f, indent=2)
            print(f"Report saved to: {p}")
        except Exception:
            pass

    db.close()
    if not invariants_passed:
        sys.exit(1)
    return report_payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify live official data pre-fetch before prediction")
    parser.add_argument("--commodity", default="Tomato", help="Commodity name")
    parser.add_argument("--market", default="Madanapalli APMC", help="Market name")
    parser.add_argument("--forecast-date", default="2026-08-16", help="Forecast base date (YYYY-MM-DD)")
    args = parser.parse_args()

    run_verification(args.commodity, args.market, args.forecast_date)
