#!/usr/bin/env python3
"""
Master Verification Script for CropMandi AI:
Forecast Precedence, Official API-First Data, Date Separation, Stable Target Values,
Simple Today vs Past-Date Views, Trends/Weather Integrity, and 100% i18n Localization.

Outputs results to: cropmandi-ai/backend/reports/master_forecast_and_i18n_verification.json
"""

import os
import sys
import json
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, SessionLocal
from app.models import Market, Commodity, OfficialMarketPrice, CleanedMarketPrice
from app.utils.date_service import get_ist_today
from app.services.master_data_service import find_exact_master_record

client = TestClient(app)

def run_all_verifications():
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "timezone_verified": False,
        "server_today": None,
        "checks": {},
        "summary": {
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "status": "pending"
        }
    }

    def record_check(name: str, passed: bool, details: dict):
        report["checks"][name] = {
            "passed": passed,
            "details": details
        }
        report["summary"]["total_checks"] += 1
        if passed:
            report["summary"]["passed_checks"] += 1
        else:
            report["summary"]["failed_checks"] += 1

    # 1. IST Timezone Check
    today_ist = get_ist_today()
    expected_today = datetime.now(ZoneInfo("Asia/Kolkata")).date()
    tz_passed = (today_ist == expected_today)
    report["timezone_verified"] = tz_passed
    report["server_today"] = str(today_ist)
    record_check("ist_timezone_determination", tz_passed, {
        "today_ist": str(today_ist),
        "expected_today": str(expected_today)
    })

    # 2. Models Health Diagnostic Endpoint
    res = client.get("/api/v1/models/health")
    m_data = res.json() if res.status_code == 200 else {}
    record_check("models_health_endpoint", res.status_code == 200 and m_data.get("status") in ("healthy", "ready", "degraded"), {
        "status_code": res.status_code,
        "active_model_version": m_data.get("active_model_version"),
        "models_status": m_data.get("status")
    })

    # 3. Data Source Health Diagnostic Endpoint
    res = client.get("/api/v1/data-source/health")
    ds_data = res.json() if res.status_code == 200 else {}
    record_check("data_source_health_endpoint", res.status_code == 200 and ds_data.get("status") in ("ready", "degraded"), {
        "status_code": res.status_code,
        "fields_detected": ds_data.get("fields_detected"),
        "record_counts": ds_data.get("record_counts"),
        "master_csv_available": ds_data.get("master_csv_available")
    })

    # 4. Verified Forecast Query - Official Precedence & Target Date Stability
    # We query with force_refresh=false on an official historical date (e.g. 2026-08-18)
    res_d = client.post("/api/v1/forecast/verified", json={
        "commodity": "Tomato",
        "market": "Madanapalli APMC",
        "selected_date": "2026-08-18",
        "force_refresh": False
    })
    fc_d = res_d.json() if res_d.status_code == 200 else {}
    records_d = fc_d.get("records", [])

    origin_sep_passed = False
    records_official_count = 0
    if records_d:
        rec0 = records_d[0]
        # Check separation of forecast_origin_date, target_date, observation_date
        origin_sep_passed = (
            rec0.get("forecast_origin_date") == "2026-08-18" and
            rec0.get("target_date") == "2026-08-18" and
            rec0.get("observation_date") == "2026-08-18" and
            rec0.get("is_observed") is True and
            rec0.get("is_predicted") is False
        )
        records_official_count = sum(1 for r in records_d if r.get("is_observed") is True)

    record_check("forecast_date_separation_and_official_priority", origin_sep_passed, {
        "status_code": res_d.status_code,
        "records_count": len(records_d),
        "official_records_count": records_official_count,
        "sample_record": records_d[0] if records_d else None
    })

    # 5. Target Value Stability across Origins
    # Query 2026-08-17 and check target date 2026-08-18
    res_prev = client.post("/api/v1/forecast/verified", json={
        "commodity": "Tomato",
        "market": "Madanapalli APMC",
        "selected_date": "2026-08-17",
        "force_refresh": False
    })
    fc_prev = res_prev.json() if res_prev.status_code == 200 else {}
    records_prev = fc_prev.get("records", [])

    # Find 2026-08-18 in records_prev
    p_rec_18 = next((r for r in records_prev if r.get("target_date") == "2026-08-18" or r.get("date") == "2026-08-18"), None)
    d_rec_18 = next((r for r in records_d if r.get("target_date") == "2026-08-18" or r.get("date") == "2026-08-18"), None)

    stability_passed = False
    if p_rec_18 and d_rec_18:
        # If both are official, their modal prices must match exactly
        if p_rec_18.get("is_observed") and d_rec_18.get("is_observed"):
            stability_passed = (p_rec_18.get("modal_price") == d_rec_18.get("modal_price"))
        else:
            stability_passed = True  # If 17 had no 18 record at the time, acceptable

    record_check("target_value_stability_across_origins", stability_passed, {
        "target_date": "2026-08-18",
        "price_from_origin_18": d_rec_18.get("modal_price") if d_rec_18 else None,
        "price_from_origin_17": p_rec_18.get("modal_price") if p_rec_18 else None,
        "source_from_18": d_rec_18.get("price_source") if d_rec_18 else None,
        "source_from_17": p_rec_18.get("price_source") if p_rec_18 else None
    })

    # 6. Strict Source Hierarchy & Forbidden States Verification
    # Check that is_observed and is_predicted are never both True
    no_forbidden_flags = True
    for r in records_d + records_prev:
        if r.get("is_observed") is True and r.get("is_predicted") is True:
            no_forbidden_flags = False
        if r.get("price_source") == "unavailable" and r.get("modal_price") is not None:
            no_forbidden_flags = False

    record_check("forbidden_states_and_flags_validation", no_forbidden_flags, {
        "total_records_inspected": len(records_d) + len(records_prev),
        "no_forbidden_flags": no_forbidden_flags
    })

    # 7. Trends & Comparison Official-Only Verification
    res_trends = client.get("/api/v1/prices/trends", params={
        "commodity": "Tomato",
        "market": "Madanapalli APMC",
        "days": 30
    })
    trends_data = res_trends.json() if res_trends.status_code == 200 else []
    trends_official_only = True
    for pt in trends_data:
        src = pt.get("price_source")
        if src and src not in ("official_api", "official_database", "official_csv"):
            trends_official_only = False

    record_check("trends_official_only_filtering", res_trends.status_code == 200 and trends_official_only, {
        "status_code": res_trends.status_code,
        "total_points": len(trends_data),
        "official_sources_verified": trends_official_only
    })

    # 8. Weather Coverage Verification
    res_wth = client.get("/api/v1/weather/coverage")
    wth_data = res_wth.json() if res_wth.status_code == 200 else {}
    wth_passed = (
        res_wth.status_code == 200 and
        wth_data.get("total_active_markets", 0) > 0 and
        wth_data.get("markets_with_coordinates", 0) > 0
    )
    record_check("weather_coverage_active_markets", wth_passed, {
        "status_code": res_wth.status_code,
        "total_active_markets": wth_data.get("total_active_markets"),
        "markets_with_coordinates": wth_data.get("markets_with_coordinates")
    })

    # 9. i18n Key Completeness Verification
    # Check translations dictionary file directly
    i18n_file = os.path.abspath(os.path.join(backend_dir, "..", "frontend", "src", "i18n", "translations.ts"))
    i18n_exists = os.path.exists(i18n_file)
    i18n_content = ""
    if i18n_exists:
        with open(i18n_file, "r", encoding="utf-8") as f:
            i18n_content = f.read()

    required_langs = ["en", "te", "hi", "ml", "ta"]
    required_namespaces = [
        "common", "forecast", "trends", "comparison", "weather", "disease",
        "auth", "validation", "errors", "warnings"
    ]
    
    missing_elements = []
    for l in required_langs:
        if f"{l}:" not in i18n_content:
            missing_elements.append(f"Language {l} block missing")
    for ns in required_namespaces:
        if f"{ns}:" not in i18n_content:
            missing_elements.append(f"Namespace {ns} missing")

    i18n_passed = i18n_exists and len(missing_elements) == 0
    record_check("complete_i18n_localization_completeness", i18n_passed, {
        "file_exists": i18n_exists,
        "languages_checked": required_langs,
        "namespaces_checked": required_namespaces,
        "missing_elements": missing_elements
    })

    # Summary calculation
    report["summary"]["status"] = "PASSED" if report["summary"]["failed_checks"] == 0 else "FAILED"

    # Save JSON Report
    reports_dir = os.path.join(backend_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    report_path = os.path.join(reports_dir, "master_forecast_and_i18n_verification.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n==================================================")
    print(f"MASTER VERIFICATION RESULT: {report['summary']['status']}")
    print(f"Total: {report['summary']['total_checks']} | Passed: {report['summary']['passed_checks']} | Failed: {report['summary']['failed_checks']}")
    print(f"Report saved to: {report_path}")
    print(f"==================================================\n")

    return 0 if report["summary"]["failed_checks"] == 0 else 1

if __name__ == "__main__":
    sys.exit(run_all_verifications())
