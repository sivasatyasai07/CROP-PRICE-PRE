import pytest
import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.ml.predict import _fallback_response, generate_3day_prediction
from app.ml.model_registry import check_model_health, get_active_model_version
from app.services.seed_service import seed_markets_and_commodities

@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    seed_markets_and_commodities(db)
    yield db
    db.close()

def test_fallback_response_with_latest_price(db_session: Session):
    """Test A: latest_price exists -> no NameError, price_source = fallback_last_observed, is_predicted = True, prediction_executed = False."""
    pred_dt = datetime.date(2026, 8, 17)
    res = _fallback_response(
        db=db_session,
        market_name="Madanapalle APMC",
        commodity_name="Tomato",
        pred_dt=pred_dt,
        snapshot_id="test_snap_001",
        latest_price=1400.0,
        latest_date_str="2026-08-16",
        reason="Model artifact not loaded for version test"
    )

    assert res is not None
    assert "feature_explanations" in res
    assert len(res["feature_explanations"]) > 0
    assert len(res["predictions"]) == 3

    for p in res["predictions"]:
        assert p["price_source"] == "fallback_last_observed"
        assert p["is_predicted"] is True
        assert p["prediction_executed"] is False
        assert p["model_predict_called"] is False
        assert p["predicted_modal_price"] == 1400.0
        assert p["interval_available"] is False


def test_fallback_response_without_latest_price(db_session: Session):
    """Test B: latest_price is None -> no NameError, price_source = unavailable, modal price = None, is_predicted = False."""
    pred_dt = datetime.date(2026, 8, 17)
    res = _fallback_response(
        db=db_session,
        market_name="Madanapalle APMC",
        commodity_name="Tomato",
        pred_dt=pred_dt,
        snapshot_id="test_snap_002",
        latest_price=None,
        latest_date_str=None,
        reason="No observed mandi price available"
    )

    assert res is not None
    assert "feature_explanations" in res
    assert len(res["feature_explanations"]) > 0
    assert len(res["predictions"]) == 3

    for p in res["predictions"]:
        assert p["price_source"] == "unavailable"
        assert p["is_predicted"] is False
        assert p["prediction_executed"] is False
        assert p["predicted_modal_price"] is None


def test_missing_model_artifact_handling(db_session: Session):
    """Test C: Model artifact is missing -> fallback response is returned safely, no exception."""
    pred_dt = datetime.date(2026, 8, 17)
    res = generate_3day_prediction(
        db=db_session,
        commodity_name="Tomato",
        market_name="Madanapalle APMC",
        prediction_date_str="2026-08-17",
        model_version="non_existent_version_9999"
    )

    assert res is not None
    assert "predictions" in res
    assert len(res["predictions"]) == 3
    for p in res["predictions"]:
        assert p["price_source"] == "fallback_last_observed"
        assert "non_existent_version_9999" in p["fallback_reason"]


def test_loaded_model_prediction(db_session: Session):
    """Test D: Model artifact loads -> trained-model result is returned, source is predicted_model."""
    active_ver = get_active_model_version(db_session)
    health = check_model_health(db_session)
    assert health["status"] == "ready"
    assert health["h1_loaded"] is True
    assert health["h2_loaded"] is True
    assert health["h3_loaded"] is True

    res = generate_3day_prediction(
        db=db_session,
        commodity_name="Tomato",
        market_name="Madanapalle APMC",
        prediction_date_str="2026-08-17"
    )

    assert res is not None
    assert "predictions" in res
    assert len(res["predictions"]) == 3
    for p in res["predictions"]:
        assert p["price_source"] == "predicted_model"
        assert p["prediction_executed"] is True
        assert p["interval_available"] is True
        assert p["predicted_modal_price"] is not None
        assert p["predicted_modal_price"] > 0
