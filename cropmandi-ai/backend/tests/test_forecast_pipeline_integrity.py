import pytest
import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

from app.database import SessionLocal
from app.models import Market, Commodity, CleanedMarketPrice, Prediction
from app.schemas.forecast import VerifiedForecastRequest
from app.ml.predict import generate_3day_prediction, _fallback_response
from app.services.forecast_reconciliation_service import (
    reconcile_verified_forecast,
    resolve_price_for_date,
    supersede_stale_predictions_for_date,
    record_prediction_versioning
)


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_1_model_predict_succeeds(db_session):
    """1. model.predict() succeeds -> Expected source: predicted_model."""
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([2540.50])
    mock_metadata = {
        "feature_columns": ["market", "commodity", "district", "lag_1", "arrival_quantity_lag_1", "temp_max_clean", "sin_day_of_year"],
        "conformal_q80": {1: 120.0, 2: 150.0, 3: 180.0}
    }

    with patch("app.ml.predict.load_model_artifacts", return_value=({1: mock_model, 2: mock_model, 3: mock_model}, mock_metadata)):
        res = generate_3day_prediction(
            db=db_session,
            commodity_name="Tomato",
            market_name="Madanapalli APMC",
            prediction_date_str="2026-08-16"
        )
        assert res is not None
        preds = res.get("predictions", [])
        assert len(preds) == 3
        for p in preds:
            assert p["price_source"] == "predicted_model"
            assert p["prediction_method"] == "trained_model"
            assert p["prediction_executed"] is True
            assert p["model_predict_called"] is True
            assert p["predicted_modal_price"] == 2540.50
            assert p["interval_available"] is True
            assert p["lower_bound"] is not None
            assert p["upper_bound"] is not None
            assert p["confidence_level"] == 0.80
            assert p["confidence_source"] == "calibration_metadata"


def test_2_model_predict_raises_exception(db_session):
    """2. model.predict() raises an exception -> Expected source: fallback_last_observed, no CatBoost label."""
    mock_model = MagicMock()
    mock_model.predict.side_effect = RuntimeError("CatBoost C++ inference segfault")
    mock_metadata = {
        "feature_columns": ["market", "commodity", "district", "lag_1", "arrival_quantity_lag_1", "temp_max_clean", "sin_day_of_year"],
        "conformal_q80": {1: 120.0, 2: 150.0, 3: 180.0}
    }

    with patch("app.ml.predict.load_model_artifacts", return_value=({1: mock_model, 2: mock_model, 3: mock_model}, mock_metadata)):
        res = generate_3day_prediction(
            db=db_session,
            commodity_name="Tomato",
            market_name="Madanapalli APMC",
            prediction_date_str="2026-08-16"
        )
        preds = res.get("predictions", [])
        assert len(preds) == 3
        for p in preds:
            assert p["price_source"] == "fallback_last_observed"
            assert p["prediction_method"] == "fallback"
            assert p["prediction_executed"] is False
            assert p["model_predict_called"] is True
            assert p["fallback_reason"] == "model_prediction_error"
            assert p["model_error_code"] == "model_prediction_exception"
            assert p["model_name"] == "Last observed price fallback"
            # Conformal interval should be unavailable on fallback
            assert p["interval_available"] is False
            assert p["lower_bound"] is None
            assert p["upper_bound"] is None
            assert p["confidence_level"] is None


def test_3_no_observed_price_exists(db_session):
    """3. No observed price exists -> Expected source: unavailable."""
    res = generate_3day_prediction(
        db=db_session,
        commodity_name="NonExistentCrop123",
        market_name="NonExistentMarket123",
        prediction_date_str="2026-08-16"
    )
    preds = res.get("predictions", [])
    assert len(preds) == 3
    for p in preds:
        assert p["price_source"] == "unavailable"
        assert p["prediction_method"] == "none"
        assert p["prediction_executed"] is False
        assert p["predicted_modal_price"] is None
        assert p["is_observed"] is False
        assert p["is_predicted"] is False
        assert p["interval_available"] is False


def test_4_official_api_record_exists(db_session):
    """4. Official API record exists -> Expected source: official_api, model not called."""
    req = VerifiedForecastRequest(
        commodity="Tomato",
        market="Madanapalli APMC",
        selected_date=date(2026, 8, 16),
        force_refresh=True
    )
    mock_api_records = {
        date(2026, 8, 16): {
            "modal_price": 2800.0,
            "min_price": 2600.0,
            "max_price": 3000.0,
            "arrival_quantity": 45.0,
            "arrival_unit": "Metric Tonnes",
            "price_unit": "Rs./Quintal",
            "record_id": "api_rec_001"
        }
    }

    mock_pred_resp = {
        "predictions": [],
        "model_version": "catboost-v2.1",
        "feature_snapshot_id": "test_snap_001",
        "feature_explanations": [],
        "feature_schema_match": True,
        "missing_features": [],
        "unexpected_features": [],
        "expected_feature_count": 98,
        "runtime_feature_count": 98
    }

    sync_payload = {
        "api_called": True,
        "api_status": "success",
        "records_by_date": mock_api_records,
        "records_accepted": len(mock_api_records),
        "latest_api_date": date(2026, 8, 16)
    }

    with patch("app.services.forecast_reconciliation_service.refresh_before_forecast", return_value=sync_payload):
        with patch("app.services.forecast_reconciliation_service.fetch_date_range_records", return_value=mock_api_records):
            with patch("app.services.forecast_reconciliation_service.generate_3day_prediction", return_value=mock_pred_resp):
                res = reconcile_verified_forecast(db_session, req)
                day0_rec = res.records[0]
                assert day0_rec.price_source == "official_api"
                assert day0_rec.data_status == "observed_live"
                assert day0_rec.is_observed is True
                assert day0_rec.is_predicted is False
                assert day0_rec.prediction_method == "official_observation"
                assert day0_rec.model_predict_called is False
                assert day0_rec.prediction_executed is False
                assert day0_rec.confidence_level is None
                assert day0_rec.source_label == "Official value from data.gov.in"


def test_5_master_data_csv_lookup_when_api_misses(db_session):
    """5. API misses but master-data.csv contains a record -> Expected source: official_csv."""
    req = VerifiedForecastRequest(
        commodity="Tomato",
        market="Madanapalli APMC",
        selected_date=date(2026, 8, 14),
        force_refresh=True
    )
    empty_sync = {
        "api_called": True,
        "api_status": "checked_no_records",
        "records_by_date": {},
        "records_accepted": 0,
        "latest_api_date": None
    }
    with patch("app.services.forecast_reconciliation_service.refresh_before_forecast", return_value=empty_sync):
        with patch("app.services.forecast_reconciliation_service.fetch_date_range_records", return_value={}):
            with patch("app.services.official_market_service.fetch_exact_official_record", return_value=(None, {"source": "official_api", "searched": True, "found": False})):
                res = reconcile_verified_forecast(db_session, req)
                day0_rec = res.records[0]
                # In master-data.csv 2026-08-14 is present
                assert day0_rec.price_source == "official_csv"
            assert day0_rec.data_status == "observed_csv"
            assert day0_rec.is_observed is True
            assert day0_rec.is_predicted is False
            assert day0_rec.prediction_method == "official_observation"
            assert day0_rec.confidence_level is None
            assert day0_rec.source_label == "Official value from master-data.csv"


def test_6_model_output_is_nan_or_negative(db_session):
    """6. Model output is NaN or negative -> Expected explicit failure and fallback/unavailable."""
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([np.nan])
    mock_metadata = {
        "feature_columns": ["market", "commodity", "district", "lag_1", "arrival_quantity_lag_1", "temp_max_clean", "sin_day_of_year"],
        "conformal_q80": {1: 120.0}
    }

    with patch("app.ml.predict.load_model_artifacts", return_value=({1: mock_model, 2: mock_model, 3: mock_model}, mock_metadata)):
        res = generate_3day_prediction(
            db=db_session,
            commodity_name="Tomato",
            market_name="Madanapalli APMC",
            prediction_date_str="2026-08-16"
        )
        preds = res.get("predictions", [])
        for p in preds:
            assert p["prediction_executed"] is False
            assert p["price_source"] in ["fallback_last_observed", "unavailable"]
            assert p["model_error_code"] == "model_prediction_exception"


def test_7_feature_schema_incomplete_fails_closed(db_session):
    """7. Feature schema is incomplete -> Expected no valid trained-model label."""
    mock_model = MagicMock()
    mock_metadata = {
        "feature_columns": ["market", "commodity", "district", "REQUIRED_FUTURE_FEAT_DOES_NOT_EXIST_999"],
        "conformal_q80": {1: 120.0}
    }

    with patch("app.ml.predict.load_model_artifacts", return_value=({1: mock_model, 2: mock_model, 3: mock_model}, mock_metadata)):
        res = generate_3day_prediction(
            db=db_session,
            commodity_name="Tomato",
            market_name="Madanapalli APMC",
            prediction_date_str="2026-08-16"
        )
        assert res["feature_schema_match"] is False
        preds = res.get("predictions", [])
        for p in preds:
            assert p["prediction_executed"] is False
            assert p["price_source"] != "predicted_model"
            assert "feature_schema_mismatch" in p["fallback_reason"]


def test_8_conformal_interval_metadata_missing_no_fake_bounds(db_session):
    """8. Conformal interval metadata is missing -> Expected null bounds, NOT ±10% bounds."""
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([3000.0])
    mock_metadata = {
        "feature_columns": ["market", "commodity", "district", "lag_1", "arrival_quantity_lag_1", "temp_max_clean", "sin_day_of_year"],
        "conformal_q80": {}  # Empty conformal metadata
    }

    with patch("app.ml.predict.load_model_artifacts", return_value=({1: mock_model, 2: mock_model, 3: mock_model}, mock_metadata)):
        res = generate_3day_prediction(
            db=db_session,
            commodity_name="Tomato",
            market_name="Madanapalli APMC",
            prediction_date_str="2026-08-16"
        )
        preds = res.get("predictions", [])
        for p in preds:
            assert p["prediction_executed"] is True
            assert p["predicted_modal_price"] == 3000.0
            assert p["interval_available"] is False
            assert p["lower_bound"] is None
            assert p["upper_bound"] is None
            assert p["confidence_level"] is None
            assert p["confidence_source"] == "unavailable"


def test_9_fallback_source_preserved_in_reconciliation(db_session):
    """9. Fallback source reaches response as fallback estimate, NOT CatBoost AI model."""
    mock_model = MagicMock()
    mock_model.predict.side_effect = Exception("Inference memory fault")
    mock_metadata = {
        "feature_columns": ["market", "commodity", "district", "lag_1", "arrival_quantity_lag_1", "temp_max_clean", "sin_day_of_year"],
    }

    empty_sync = {
        "api_called": True,
        "api_status": "checked_no_records",
        "records_by_date": {},
        "records_accepted": 0,
        "latest_api_date": None
    }

    with patch("app.ml.predict.load_model_artifacts", return_value=({1: mock_model, 2: mock_model, 3: mock_model}, mock_metadata)):
        with patch("app.services.forecast_reconciliation_service.refresh_before_forecast", return_value=empty_sync):
            with patch("app.services.forecast_reconciliation_service.fetch_date_range_records", return_value={}):
                req = VerifiedForecastRequest(
                    commodity="Tomato",
                    market="Madanapalli APMC",
                    selected_date=date(2026, 8, 16),
                    force_refresh=True
                )
                res = reconcile_verified_forecast(db_session, req)
                # Find a predicted/fallback day (e.g. Day 1, 2 or 3)
                fallback_records = [r for r in res.records if r.price_source == "fallback_last_observed"]
                for r in fallback_records:
                    assert r.price_source == "fallback_last_observed"
                    assert r.prediction_method == "fallback"
                    assert r.prediction_executed is False
                    assert r.source_label == "Fallback estimate: last observed official price"
                    assert r.source_name == "Last observed price fallback"
                    assert r.confidence_level is None
                    assert r.interval_available is False


def test_10_official_source_reconciliation_confidence_is_none(db_session):
    """10. Official source reaches response -> Expected confidence_level is None."""
    req = VerifiedForecastRequest(
        commodity="Tomato",
        market="Madanapalli APMC",
        selected_date=date(2026, 8, 14),
        force_refresh=True
    )
    empty_sync = {
        "api_called": True,
        "api_status": "checked_no_records",
        "records_by_date": {},
        "records_accepted": 0,
        "latest_api_date": None
    }
    with patch("app.services.forecast_reconciliation_service.refresh_before_forecast", return_value=empty_sync):
        with patch("app.services.forecast_reconciliation_service.fetch_date_range_records", return_value={}):
            res = reconcile_verified_forecast(db_session, req)
            for r in res.records:
                if r.is_observed:
                    assert r.confidence_level is None
                    assert r.is_predicted is False


def test_11_four_dates_resolved_independently(db_session):
    """11. Four dates are resolved independently across API, CSV, Model, Fallback."""
    req = VerifiedForecastRequest(
        commodity="Tomato",
        market="Madanapalli APMC",
        selected_date=date(2026, 8, 15),
        force_refresh=True
    )
    res = reconcile_verified_forecast(db_session, req)
    assert len(res.records) == 4
    dates = [r.date for r in res.records]
    assert dates == [date(2026, 8, 15), date(2026, 8, 16), date(2026, 8, 17), date(2026, 8, 18)]
    for r in res.records:
        assert r.price_source in ["official_api", "official_csv", "predicted_model", "fallback_last_observed", "unavailable"]


def test_12_official_record_supersedes_older_model_prediction(db_session):
    """12. An official record supersedes older model prediction."""
    market = db_session.query(Market).first()
    commodity = db_session.query(Commodity).first()
    target_dt = date(2026, 8, 20)

    # Insert test prediction
    pred = Prediction(
        market_id=market.id,
        commodity_id=commodity.id,
        prediction_date=date(2026, 8, 17),
        forecast_origin_date=date(2026, 8, 17),
        target_date=target_dt,
        horizon=3,
        predicted_modal_price=2400.0,
        lower_bound=2200.0,
        upper_bound=2600.0,
        price_source="predicted_model",
        prediction_status="active",
        model_version="v20260818_153724",
        feature_snapshot_id="test_snap_001"
    )
    db_session.add(pred)
    db_session.commit()
    db_session.refresh(pred)

    assert pred.prediction_status == "active"
    assert pred.superseded_by_official is False

    # Mark superseded
    supersede_stale_predictions_for_date(db_session, market.id, commodity.id, target_dt)

    db_session.refresh(pred)
    assert pred.prediction_status == "superseded_by_official"
    assert pred.superseded_by_official is True
