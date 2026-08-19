import os
import sys
import json
import argparse
from datetime import datetime, date
from typing import Dict, Any, List, Optional
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.services.master_data_service import get_master_data_stats, find_exact_master_record

API_BASE_URL = "http://127.0.0.1:8000"

SUPPORTED_CROPS = [
    "Tomato", "Potato", "Brinjal", "Carrot", "Cabbage", "Beetroot",
    "Paddy", "Maize", "Jowar", "Groundnut", "Sunflower", "Red gram"
]

CONFIGURED_MARKETS = [
    "Madanapalli APMC", "Kalikiri APMC", "Punganur APMC", "Palamaner APMC",
    "Banaganapalli APMC", "Kurnool APMC", "Adoni APMC", "Anantapur APMC",
    "Vayalapadu APMC", "Valmikipuram APMC", "Mulakalacheruvu APMC", "Kuppam APMC"
]


def verify_single_combination(commodity: str, market: str, selected_date: str) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/forecast/verified"
    req_body = {
        "commodity": commodity,
        "market": market,
        "selected_date": selected_date,
        "force_refresh": True,
        "request_id": f"audit_{Date.now() if 'Date' in globals() else datetime.now().timestamp()}"
    }

    try:
        res = requests.post(url, json=req_body, timeout=20)
    except Exception as exc:
        return {"status": "FAILED", "error": str(exc), "commodity": commodity, "market": market, "date": selected_date}

    if res.status_code != 200:
        return {"status": "FAILED", "error": f"HTTP {res.status_code}: {res.text}", "commodity": commodity, "market": market, "date": selected_date}

    data = res.json()
    records = data.get("records", [])
    if not records:
        return {"status": "FAILED", "error": "No records returned", "commodity": commodity, "market": market, "date": selected_date}

    date_results = []
    all_passed = True

    for r in records:
        r_date = r.get("date")
        modal_p = r.get("modal_price")
        price_src = r.get("price_source")
        data_stat = r.get("data_status")
        is_obs = r.get("is_observed")
        is_pred = r.get("is_predicted")
        src_label = r.get("source_label")
        trace = r.get("lookup_trace", [])

        # Consistency Checks
        valid = True
        reason = []

        if price_src == "official_api":
            if not (is_obs is True and is_pred is False and data_stat == "observed_live"):
                valid = False
                reason.append("official_api must have is_observed=True, is_predicted=False, data_status=observed_live")
        elif price_src == "official_csv":
            if not (is_obs is True and is_pred is False and data_stat == "observed_csv"):
                valid = False
                reason.append("official_csv must have is_observed=True, is_predicted=False, data_status=observed_csv")
        elif price_src == "predicted":
            if not (is_obs is False and is_pred is True and data_stat == "predicted_fallback"):
                valid = False
                reason.append("predicted must have is_observed=False, is_predicted=True, data_status=predicted_fallback")
        elif price_src == "unavailable":
            if not (is_obs is False and is_pred is False and modal_p is None and data_stat == "unavailable"):
                valid = False
                reason.append("unavailable must have modal_price=None, is_observed=False, is_predicted=False")
        else:
            valid = False
            reason.append(f"Invalid price_source: {price_src}")

        if not valid:
            all_passed = False

        date_results.append({
            "date": r_date,
            "modal_price": modal_p,
            "price_source": price_src,
            "data_status": data_stat,
            "is_observed": is_obs,
            "is_predicted": is_pred,
            "source_label": src_label,
            "api_checked": r.get("api_checked", True),
            "api_record_found": r.get("api_record_found", False),
            "master_csv_checked": r.get("master_csv_checked", False),
            "master_csv_record_found": r.get("master_csv_record_found", False),
            "prediction_generated": r.get("prediction_generated", False),
            "valid": valid,
            "errors": reason
        })

    return {
        "commodity": commodity,
        "market": market,
        "selected_date": selected_date,
        "status": "PASS" if all_passed else "FAIL",
        "dates": date_results,
        "summary": data.get("summary", {})
    }


def main():
    parser = argparse.ArgumentParser(description="Verify CropMandi AI Price Source Priority & Precedence")
    parser.add_argument("--commodity", type=str, default="Tomato")
    parser.add_argument("--market", type=str, default="Madanapalli APMC")
    parser.add_argument("--selected-date", type=str, default="2026-08-14")
    parser.add_argument("--all-supported-crops", action="store_true")
    parser.add_argument("--all-configured-markets", action="store_true")
    args = parser.parse_args()

    print("==================================================")
    print("  CROPMANDI AI — PRICE SOURCE PRIORITY AUDIT")
    print("==================================================")

    crops = SUPPORTED_CROPS if args.all_supported_crops else [args.commodity]
    markets = CONFIGURED_MARKETS if args.all_configured_markets else [args.market]
    sel_date = args.selected_date

    stats = get_master_data_stats()
    print(f"Authoritative master-data.csv loaded: {stats.get('total_rows_loaded', 0)} rows, {stats.get('unique_keys', 0)} unique keys.")

    all_reports = []
    passed_count = 0
    total_count = 0

    for c in crops:
        for m in markets:
            total_count += 1
            res = verify_single_combination(c, m, sel_date)
            all_reports.append(res)
            if res.get("status") == "PASS":
                passed_count += 1

            print(f"\nCommodity: {c} | Market: {m} | Date: {sel_date}")
            for d_info in res.get("dates", []):
                print(f"  Date: {d_info.get('date')}")
                print(f"    API searched:              {'Yes' if d_info.get('api_checked') else 'No'}")
                print(f"    API exact record found:    {'Yes' if d_info.get('api_record_found') else 'No'}")
                print(f"    master-data.csv searched:  {'Yes' if d_info.get('master_csv_checked') else 'No'}")
                print(f"    master-data.csv record:    {'Yes' if d_info.get('master_csv_record_found') else 'No'}")
                print(f"    Prediction generated:      {'Yes' if d_info.get('prediction_generated') else 'No'}")
                print(f"    Final modal price:         {d_info.get('modal_price')}")
                print(f"    Final source:              {d_info.get('price_source')}")
                print(f"    is_observed:               {d_info.get('is_observed')}")
                print(f"    is_predicted:              {d_info.get('is_predicted')}")
                print(f"    Verification:              {'PASS' if d_info.get('valid') else 'FAIL'}")

    report_path = os.path.join(BASE_DIR, "data", "price_source_verification_report.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "audit_timestamp": datetime.now().isoformat(),
            "total_tested": total_count,
            "passed": passed_count,
            "failed": total_count - passed_count,
            "reports": all_reports
        }, f, indent=2)

    print("\n==================================================")
    print(f"  AUDIT SUMMARY: {passed_count}/{total_count} PASSED")
    print(f"  Report saved to: {report_path}")
    print("==================================================")

    if passed_count < total_count:
        sys.exit(1)


if __name__ == "__main__":
    main()
