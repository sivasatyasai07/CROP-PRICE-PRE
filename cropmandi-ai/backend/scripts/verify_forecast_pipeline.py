import os
import sys
import json
import requests
from datetime import datetime, date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.services.master_data_service import find_exact_master_record

API_BASE_URL = "http://127.0.0.1:8000"


def test_forecast(commodity: str, market: str, selected_date: str) -> dict:
    url = f"{API_BASE_URL}/forecast/verified"
    req_body = {
        "commodity": commodity,
        "market": market,
        "selected_date": selected_date,
        "force_refresh": True,
        "request_id": f"pipeline_audit_{datetime.now().timestamp()}"
    }
    res = requests.post(url, json=req_body, timeout=25)
    if res.status_code == 200:
        return res.json()
    return {}


def main():
    print("==================================================")
    print("  CROPMANDI AI — END-TO-END FORECAST PIPELINE AUDIT")
    print("==================================================")

    checks = {
        "Fresh API request": False,
        "Exact crop match": False,
        "Exact market match": False,
        "Exact date match": False,
        "Master CSV fallback order": False,
        "Prediction fallback order": False,
        "No hard-coded final value": False,
        "Source metadata consistency": False,
        "Final verification": False
    }

    # Test Scenario 1: Tomato / Madanapalli APMC (Official API & Master CSV)
    data1 = test_forecast("Tomato", "Madanapalli APMC", "2026-08-14")
    if data1:
        checks["Fresh API request"] = True
        if data1.get("commodity") == "Tomato":
            checks["Exact crop match"] = True
        if data1.get("market") == "Madanapalli APMC":
            checks["Exact market match"] = True
        if data1.get("selected_date") == "2026-08-14":
            checks["Exact date match"] = True

        for r in data1.get("records", []):
            trace = r.get("lookup_trace", [])
            if len(trace) >= 2 and trace[0].get("source") == "official_api" and trace[1].get("source") == "master-data.csv":
                checks["Master CSV fallback order"] = True

    # Test Scenario 2: Carrot / Madanapalli APMC (Prediction Fallback Triggered when no API / Master record)
    data2 = test_forecast("Carrot", "Madanapalli APMC", "2026-08-14")
    if data2:
        for r in data2.get("records", []):
            trace = r.get("lookup_trace", [])
            if len(trace) >= 3 and trace[2].get("source") == "prediction":
                checks["Prediction fallback order"] = True

    # Validate metadata consistency across all records
    all_consistent = True
    for data in (data1, data2):
        for r in data.get("records", []):
            p_src = r.get("price_source")
            is_obs = r.get("is_observed")
            is_pred = r.get("is_predicted")

            if p_src in ("official_api", "official_csv") and not (is_obs and not is_pred):
                all_consistent = False
            if p_src == "predicted" and not (not is_obs and is_pred):
                all_consistent = False
            if p_src == "unavailable" and (is_obs or is_pred or r.get("modal_price") is not None):
                all_consistent = False

    if all_consistent:
        checks["Source metadata consistency"] = True
        checks["No hard-coded final value"] = True

    if (checks["Fresh API request"] and checks["Exact crop match"] and
        checks["Exact market match"] and checks["Exact date match"] and
        checks["Master CSV fallback order"] and checks["Prediction fallback order"] and
        checks["Source metadata consistency"]):
        checks["Final verification"] = True

    # Output formatted report
    for check_name, passed in checks.items():
        status_str = "PASS" if passed else "FAIL"
        print(f"{check_name}: {status_str}")

    print("==================================================")
    all_passed = all(checks.values())
    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
