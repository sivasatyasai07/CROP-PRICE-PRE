import os
import sys
import json
import argparse
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.abspath("backend"))
sys.path.insert(0, os.path.abspath("cropmandi-ai/backend"))
sys.path.insert(0, os.path.abspath("."))

from app.database import SessionLocal
from app.config import settings
from app.utils.date_service import parse_internal_date, format_api_date, get_ist_today, get_date_sequence
from app.services.official_market_service import build_api_url, fetch_paginated_records, normalize_api_record, find_exact_record
from app.services.master_data_service import find_exact_master_record
from app.schemas.forecast import VerifiedForecastRequest
from app.services.forecast_reconciliation_service import reconcile_verified_forecast


def run_dynamic_filter_verification(state: str, district: str, market: str, commodity: str, selected_date_str: str):
    print("=" * 80)
    print("DATA.GOV.IN DYNAMIC FILTER & EXACT RECORD VERIFICATION AUDIT")
    print("=" * 80)

    db = SessionLocal()
    target_dt = parse_internal_date(selected_date_str) or datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    today_ist = get_ist_today()
    sequence_dates = get_date_sequence(target_dt, 4)

    # 1. Display Sanitized Query Parameters
    endpoint_url, params, safe_log_url = build_api_url(
        state=state,
        district=district,
        market=market,
        commodity=commodity,
        target_date=target_dt
    )

    print(f"1. Configuration & Security:")
    print(f"   Resource ID: {settings.DATA_GOV_RESOURCE_ID}")
    print(f"   Sanitized Endpoint URL: {safe_log_url}")
    print(f"   API Key: [PROTECTED BACKEND SECRET - NOT LOGGED]")
    print(f"   Server Today (IST): {today_ist}")
    print("-" * 80)

    print(f"2. Requested Runtime Parameters:")
    print(f"   State: {state}")
    print(f"   District: {district}")
    print(f"   Market: {market}")
    print(f"   Commodity: {commodity}")
    print(f"   Selected Base Date (ISO): {target_dt}")
    print("-" * 80)

    # 2. Converted API Dates for 4-day Sequence
    print("3. Converted data.gov.in Filter Dates (DD/MM/YYYY):")
    for idx, d in enumerate(sequence_dates):
        print(f"   D{idx} ({d.isoformat()}) -> filters[arrival_date] = {format_api_date(d)}")
    print("-" * 80)

    # 3. Direct Live API Check for each date
    print("4. Direct API Response & Exact Record Matching Per Date:")
    all_passed = True
    actual_fields_detected = []
    per_date_results = []

    for idx, d in enumerate(sequence_dates):
        d_api_str = format_api_date(d)
        d_endpoint, d_params, d_safe_url = build_api_url(
            state=state,
            district=district,
            market=market,
            commodity=commodity,
            target_date=d
        )

        http_status, raw_records, error = fetch_paginated_records(d_endpoint, d_params, d_safe_url, max_pages=1)
        if raw_records and not actual_fields_detected:
            actual_fields_detected = list(raw_records[0].keys())

        norm_records = []
        for raw in raw_records:
            norm = normalize_api_record(raw, db)
            if norm:
                norm_records.append(norm)

        matched, rejected = find_exact_record(norm_records, commodity, market, d, district, state)

        # CSV check if API missed
        csv_res = find_exact_master_record(commodity=commodity, market=market, target_date=d, state=state, district=district)
        csv_found = csv_res.record is not None and csv_res.is_valid

        per_date_results.append({
            "date": d.isoformat(),
            "api_filter_date": d_api_str,
            "http_status": http_status,
            "raw_records_count": len(raw_records),
            "exact_api_record_found": matched is not None,
            "matched_api_record": matched,
            "rejected_records_count": len(rejected),
            "rejected_reasons": [r.get("reason") for r in rejected[:3]],
            "csv_record_found": csv_found,
            "csv_record": csv_res.record if csv_found else None,
            "error": error
        })

        print(f"   Date D{idx} [{d}] ({d_api_str}):")
        print(f"     HTTP Status: {http_status} | Raw Records: {len(raw_records)}")
        if matched:
            print(f"     [MATCH FOUND] Official Modal Price: Rs. {matched['modal_price']}")
        else:
            print(f"     [NO EXACT API MATCH] Status: {'No records for date' if http_status == 200 else f'API Error ({error})'}")
            if rejected:
                print(f"     Rejected Records: {len(rejected)} (e.g. {rejected[0].get('reason')})")
            if csv_found:
                print(f"     [CSV FALLBACK FOUND] Modal Price from master-data.csv: Rs. {csv_res.record.get('modal_price')}")
            else:
                print(f"     [CSV MISS] Not found in master-data.csv -> Will use ML Prediction")

    print("-" * 80)
    print(f"5. Actual API Fields Detected: {actual_fields_detected if actual_fields_detected else 'None (Empty response or API timeout)'}")
    print("-" * 80)

    # 4. Full Verified Forecast Reconciliation Pipeline Run
    print("6. Executing Full Reconciled Verified Forecast:")
    req = VerifiedForecastRequest(
        state=state,
        district=district,
        commodity=commodity,
        market=market,
        selected_date=target_dt,
        force_refresh=True
    )

    resp = reconcile_verified_forecast(db, req)

    for idx, r in enumerate(resp.records):
        print(f"   Date {idx} [{r.date}] ({format_api_date(r.date)}):")
        print(f"     Final Price Source: {r.price_source}")
        print(f"     Data Status: {r.data_status}")
        print(f"     Modal Price: Rs. {r.modal_price}" if r.modal_price is not None else "     Modal Price: None")
        print(f"     Is Observed: {r.is_observed} | Is Predicted: {r.is_predicted}")
        print(f"     Prediction Method: {r.prediction_method}")
        print(f"     Source Label: {r.source_label}")

        trace_steps = r.lookup_trace or []
        api_step = next((s for s in trace_steps if s.get("source") == "official_api"), {})
        csv_step = next((s for s in trace_steps if s.get("source") in ["official_csv", "master-data.csv"]), {})
        pred_step = next((s for s in trace_steps if s.get("source") in ["predicted_model", "prediction", "fallback_last_observed", "unavailable"]), {})

        print(f"     Trace: API={api_step.get('status')} | CSV={csv_step.get('status')} | ML={pred_step.get('status')}")

        # Invariant checks
        if r.price_source == "official_api" and (not r.is_observed or r.is_predicted):
            print("     [ERROR] official_api record mislabeled!")
            all_passed = False
        if r.price_source == "official_csv" and (not r.is_observed or r.is_predicted):
            print("     [ERROR] official_csv record mislabeled!")
            all_passed = False
        if r.price_source == "predicted_model" and (r.is_observed or not r.is_predicted):
            print("     [ERROR] predicted_model record mislabeled!")
            all_passed = False

    print("-" * 80)
    print(f"AUDIT RESULT: {'PASSED' if all_passed else 'FAILED'}")
    print("=" * 80)

    report_payload = {
        "report_name": "Dynamic Filter & Exact Record Verification Report",
        "generated_at": datetime.now().isoformat(),
        "status": "PASSED" if all_passed else "FAILED",
        "requested": {
            "state": state,
            "district": district,
            "market": market,
            "commodity": commodity,
            "selected_date": target_dt.isoformat()
        },
        "actual_fields_detected": actual_fields_detected,
        "per_date_results": per_date_results,
        "reconciled_records": [r.model_dump() if hasattr(r, "model_dump") else r.dict() for r in resp.records],
        "summary": resp.summary
    }

    out_paths = [
        os.path.abspath("reports/dynamic_filter_verification_report.json"),
        os.path.abspath("../reports/dynamic_filter_verification_report.json"),
        os.path.abspath("cropmandi-ai/reports/dynamic_filter_verification_report.json")
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
    parser = argparse.ArgumentParser(description="Verify dynamic data.gov.in filters and exact record validation")
    parser.add_argument("--state", default="Andhra Pradesh", help="State name")
    parser.add_argument("--district", default="Annamayya", help="District name")
    parser.add_argument("--market", default="Madanapalli", help="Market name")
    parser.add_argument("--commodity", default="Tomato", help="Commodity name")
    parser.add_argument("--selected-date", default="2026-08-17", help="Selected date (YYYY-MM-DD)")
    args = parser.parse_args()

    run_dynamic_filter_verification(args.state, args.district, args.market, args.commodity, args.selected_date)
