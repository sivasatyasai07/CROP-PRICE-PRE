import pytest
from datetime import date
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.forecast import VerifiedForecastRequest
from app.routers.forecast import verified_forecast


def test_verified_forecast_precedence():
    db = SessionLocal()
    try:
        # Test: 3-day forecast starting from selected_date (2026-08-14) -> next 3 days: Aug 15, Aug 16 (Sunday), Aug 17
        req = VerifiedForecastRequest(
            commodity="Tomato",
            market="Madanapalli APMC",
            selected_date=date(2026, 8, 14),
            force_refresh=True
        )
        res = verified_forecast(req, db)
        assert res.commodity == "Tomato"
        assert res.market == "Madanapalli APMC"
        # Must return 4 forecast sequence records [D, D+1, D+2, D+3]
        assert len(res.records) == 4
        
        assert str(res.records[0].date) == "2026-08-14"
        assert str(res.records[1].date) == "2026-08-15"
        assert str(res.records[2].date) == "2026-08-16"
        assert str(res.records[3].date) == "2026-08-17"

        # Verify that Sunday (Aug 16) is NOT dropped or marked unavailable, but has a price (official or predicted)
        sunday_rec = res.records[2]
        assert sunday_rec.modal_price is not None
        assert sunday_rec.modal_price > 0
        assert sunday_rec.price_source in ["official_api", "official_csv", "predicted_model", "fallback_last_observed", "predicted"]

        # Verify metadata fields
        for r in res.records:
            assert r.price_source in ["official_api", "official_csv", "predicted_model", "fallback_last_observed", "fallback_rolling_average", "unavailable", "predicted"]
            assert hasattr(r, "is_observed")
            assert hasattr(r, "is_predicted")
            if r.is_observed:
                assert r.price_source in ["official_api", "official_csv"]
                assert r.is_predicted is False
            elif r.is_predicted:
                assert r.price_source in ["predicted_model", "fallback_last_observed", "fallback_rolling_average", "predicted"]
                assert r.is_observed is False

    finally:
        db.close()


def test_predict_every_day_without_sunday_holiday_exclusion():
    db = SessionLocal()
    try:
        # Request a date window that includes Sunday Aug 16, 2026
        req = VerifiedForecastRequest(
            commodity="Tomato",
            market="Madanapalli APMC",
            selected_date=date(2026, 8, 15),
            force_refresh=True
        )
        res = verified_forecast(req, db)
        # Sequence: Aug 15, Aug 16 (Sunday), Aug 17, Aug 18
        assert len(res.records) == 4
        for r in res.records:
            # Every record has a valid price (official or predicted)
            assert r.modal_price is not None
            assert r.modal_price > 0
            assert r.price_source != "unavailable"
    finally:
        db.close()
