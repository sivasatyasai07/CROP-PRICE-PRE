import os
import sys
import json
import argparse
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("backend"))

from app.database import SessionLocal
from app.config import settings
from app.schemas.forecast import VerifiedForecastRequest
from app.services.forecast_reconciliation_service import reconcile_verified_forecast
from app.services.date_service import get_ist_today


def run_dynamic_verification(state: str, district: str, market: str, commodity: str, selected_date_str: str):
    print("=" * 70)
    print("DYNAMIC DATA.GOV.IN FETCH & 4-DAY SEQUENCE VERIFICATION")
    print("=" * 70)

    db = SessionLocal()
    target_dt = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    today_ist = get_ist_today()

    print(f"Requested State: {state}")
    print(f"Requested District: {district}")
    print(f"Requested Market: {market}")
    print(f"Requested Commodity: {commodity}")
    print(f"Selected Date: {target_dt}")
    print(f"Server Today (IST): {today_ist}")
    print("-" * 70)

    req = VerifiedForecastRequest(
        state=state,
        district=district,
        commodity=commodity,
        market=market,
        selected_date=target_dt,
        force_refresh=True
    )

    resp = reconcile_verified_forecast(db, req)

    print("Per-Date Lookup & Priority Verification:")
    print("-" * 70)

    all_passed = True

    for idx, r in enumerate(resp.records):
        formatted_d = r.date.strftime("%d/%m/%Y")
        print(f"Date {idx} [{r.date}] ({formatted_d}):")
        print(f"  Final Price Source: {r.price_source}")
        print(f"  Data Status: {r.data_status}")
        print(f"  Modal Price: Rs. {r.modal_price}" if r.modal_price is not None else "  Modal Price: None")
        print(f"  Is Observed: {r.is_observed} | Is Predicted: {r.is_predicted}")
        print(f"  Prediction Method: {r.prediction_method}")
        print(f"  Source Label: {r.source_label}")

        # Inspect lookup trace
        trace_steps = r.lookup_trace or []
        api_step = next((s for s in trace_steps if s.get("source") == "official_api"), {})
        csv_step = next((s for s in trace_steps if s.get("source") in ["official_csv", "master-data.csv"]), {})
        pred_step = next((s for s in trace_steps if s.get("source") in ["predicted_model", "prediction", "fallback_last_observed", "unavailable"]), {})

        print(f"  Lookup Trace:")
        print(f"    - Official API: Searched={api_step.get('searched')}, Found={api_step.get('found')}, Status={api_step.get('status')}")
        print(f"    - master-data.csv: Searched={csv_step.get('searched')}, Found={csv_step.get('found')}, Status={csv_step.get('status')}")
        print(f"    - Model Prediction: Searched={pred_step.get('searched')}, Found={pred_step.get('found')}, Status={pred_step.get('status')}")

        # Validate Priority Invariants
        if r.price_source == "official_api":
            if not r.is_observed or r.is_predicted or r.prediction_executed:
                print("  [ERROR] official_api record incorrectly flagged as predicted!")
                all_passed = False
        elif r.price_source == "official_csv":
            if not r.is_observed or r.is_predicted or r.prediction_executed:
                print("  [ERROR] official_csv record incorrectly flagged as predicted!")
                all_passed = False
        elif r.price_source == "predicted_model":
            if r.is_observed or not r.is_predicted or not r.prediction_executed:
                print("  [ERROR] predicted_model record incorrectly flagged as observed!")
                all_passed = False
        print("-" * 70)

    print(f"Overall Forecast Integrity Status: {'PASSED' if all_passed else 'FAILED'}")
    print("=" * 70)

    report_payload = {
        "report_name": "Dynamic data.gov.in Fetch Verification Report",
        "generated_at": datetime.now().isoformat(),
        "status": "PASSED" if all_passed else "FAILED",
        "requested_state": state,
        "requested_district": district,
        "requested_market": market,
        "requested_commodity": commodity,
        "selected_date": str(target_dt),
        "records": [r.model_dump() if hasattr(r, "model_dump") else r.dict() for r in resp.records],
        "summary": resp.summary
    }

    out_paths = [
        os.path.abspath("reports/dynamic_data_gov_fetch_verification_report.json"),
        os.path.abspath("../reports/dynamic_data_gov_fetch_verification_report.json"),
        os.path.abspath("cropmandi-ai/reports/dynamic_data_gov_fetch_verification_report.json")
    ]
    for p in out_paths:
        try:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(report_payload, f, indent=2, default=str)
        except Exception:
            pass

    db.close()
    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify dynamic data.gov.in fetch and 4-date sequence resolution")
    parser.add_argument("--state", default="Andhra Pradesh", help="State name")
    parser.add_argument("--district", default="Annamayya", help="District name")
    parser.add_argument("--market", default="Madanapalli", help="Market name")
    parser.add_argument("--commodity", default="Tomato", help="Commodity name")
    parser.add_argument("--selected-date", default="2026-08-17", help="Selected date (YYYY-MM-DD)")
    args = parser.parse_args()

    run_dynamic_verification(args.state, args.district, args.market, args.commodity, args.selected_date)
