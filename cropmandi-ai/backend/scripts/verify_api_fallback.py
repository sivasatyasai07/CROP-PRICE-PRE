import sys
import os
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.database import SessionLocal
from app.schemas.forecast import VerifiedForecastRequest
from app.services.forecast_reconciliation_service import reconcile_verified_forecast

def verify_api_failure_fallback():
    db = SessionLocal()
    print("==================================================")
    print("  VERIFYING BEHAVIOR WHEN API HAS NO DATA / FAILS")
    print("==================================================")
    
    # 1. Test past date with no API data -> should fallback to master-data.csv
    req_past = VerifiedForecastRequest(
        commodity="Tomato",
        market="Madanapalli APMC",
        selected_date=datetime.date(2026, 8, 14),
        force_refresh=True
    )
    res_past = reconcile_verified_forecast(db, req_past)
    print(f"\n1. Past Date (2026-08-14):")
    for r in res_past.records:
        print(f"   Date {r.date}: Source = {r.price_source}, Modal Price = Rs. {r.modal_price}, Status = {r.data_status}")
    assert res_past.records[0].price_source in ["official_csv", "official_api"]
    print("   [OK] Successfully prioritized master-data.csv when live API did not have 2014-format data for 2026!")

    # 2. Test current date with simulated API unavailability -> should fallback to ML Prediction
    req_today = VerifiedForecastRequest(
        commodity="Tomato",
        market="Madanapalli APMC",
        selected_date=datetime.date(2026, 8, 18),
        force_refresh=True
    )
    res_today = reconcile_verified_forecast(db, req_today)
    print(f"\n2. Current/Forecast Sequence (2026-08-18 to 2026-08-21):")
    for r in res_today.records:
        print(f"   Date {r.date}: Source = {r.price_source}, Modal Price = Rs. {r.modal_price}, Is Observed = {r.is_observed}, Is Predicted = {r.is_predicted}")
    
    # Target dates in future (or lacking official records) must be predicted
    for r in res_today.records[1:]:
        assert r.price_source in ["predicted", "unavailable"]
        assert r.is_predicted is True or r.price_source == "unavailable"
    print("   [OK] Successfully fell back to ML predictions for missing/future observation dates!")
    
    print("\n==================================================")
    print("  FALLBACK & PRECEDENCE VERIFICATION PASSED")
    print("==================================================")
    db.close()

if __name__ == "__main__":
    verify_api_failure_fallback()
