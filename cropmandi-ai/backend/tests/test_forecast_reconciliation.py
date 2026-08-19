import pytest
from datetime import date
from app.database import SessionLocal
from app.schemas.forecast import VerifiedForecastRequest
from app.services.forecast_reconciliation_service import reconcile_verified_forecast


def test_forecast_reconciliation_hierarchy():
    db = SessionLocal()
    try:
        req = VerifiedForecastRequest(
            commodity="Tomato",
            market="Madanapalli APMC",
            selected_date=date(2026, 8, 16),
            force_refresh=True
        )
        res = reconcile_verified_forecast(db, req)

        assert res.commodity == "Tomato"
        assert res.market == "Madanapalli APMC"
        # Must return 4 forecast sequence records (D, D+1, D+2, D+3)
        assert len(res.records) == 4

        # Verify metadata fields on returned records
        for r in res.records:
            assert r.price_source in ["official_api", "official_csv", "predicted_model", "fallback_last_observed", "fallback_rolling_average", "unavailable", "predicted"]
            assert r.data_status in ["observed_live", "observed_csv", "predicted_model", "predicted_fallback", "fallback_last_observed", "unavailable"]
            assert hasattr(r, "is_observed")
            assert hasattr(r, "is_predicted")
            assert hasattr(r, "source_label")
            assert hasattr(r, "lookup_trace")
            assert isinstance(r.lookup_trace, list)
            assert len(r.lookup_trace) >= 1

    finally:
        db.close()

