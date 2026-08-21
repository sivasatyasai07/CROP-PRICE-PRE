import pytest
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, SessionLocal
from app.utils.date_service import get_ist_today
from app.models import Market, Commodity, OfficialMarketPrice

client = TestClient(app)

def test_1_server_today_determination():
    """Verify Asia/Kolkata timezone is used for server_today."""
    today_ist = get_ist_today()
    expected = datetime.now(ZoneInfo("Asia/Kolkata")).date()
    assert today_ist == expected


def test_2_models_health_check():
    """Verify GET /api/v1/models/health returns model status and active version."""
    res = client.get("/api/v1/models/health")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "active_model_version" in data
    assert data["status"] in ("healthy", "ready", "degraded")


def test_3_data_source_health_check():
    """Verify GET /api/v1/data-source/health returns diagnostics without exposing secrets."""
    res = client.get("/api/v1/data-source/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("ready", "degraded")
    assert "fields_detected" in data
    assert "record_counts" in data
    assert "DATA_GOV_API_KEY" not in str(data)


def test_4_official_date_lookup_and_separation():
    """Verify target_date, forecast_origin_date, and observation_date separation."""
    res = client.post("/api/v1/forecast/verified", json={
        "commodity": "Tomato",
        "market": "Madanapalli APMC",
        "selected_date": "2026-08-18",
        "force_refresh": False
    })
    assert res.status_code == 200
    data = res.json()
    assert data["selected_date"] == "2026-08-18"
    assert len(data["records"]) >= 4

    rec0 = data["records"][0]
    assert rec0["forecast_origin_date"] == "2026-08-18"
    assert rec0["target_date"] == "2026-08-18"
    assert rec0["observation_date"] == "2026-08-18"
    assert rec0["is_observed"] is True
    assert rec0["is_predicted"] is False


def test_5_stable_target_values_across_origins():
    """Target date D has identical official value whether origin is D or D-1."""
    res_origin18 = client.post("/api/v1/forecast/verified", json={
        "commodity": "Tomato",
        "market": "Madanapalli APMC",
        "selected_date": "2026-08-18",
        "force_refresh": False
    })
    assert res_origin18.status_code == 200
    data18 = res_origin18.json()
    rec18_from_18 = next(r for r in data18["records"] if r.get("target_date") == "2026-08-18" or r.get("date") == "2026-08-18")

    res_origin17 = client.post("/api/v1/forecast/verified", json={
        "commodity": "Tomato",
        "market": "Madanapalli APMC",
        "selected_date": "2026-08-17",
        "force_refresh": False
    })
    assert res_origin17.status_code == 200
    data17 = res_origin17.json()
    rec18_from_17 = next(r for r in data17["records"] if r.get("target_date") == "2026-08-18" or r.get("date") == "2026-08-18")

    if rec18_from_18.get("is_observed") and rec18_from_17.get("is_observed"):
        assert rec18_from_18["modal_price"] == rec18_from_17["modal_price"]


def test_6_no_forbidden_flag_combinations():
    """Ensure is_observed and is_predicted are never both True."""
    res = client.post("/api/v1/forecast/verified", json={
        "commodity": "Tomato",
        "market": "Madanapalli APMC",
        "selected_date": "2026-08-18",
        "force_refresh": False
    })
    assert res.status_code == 200
    data = res.json()
    for rec in data["records"]:
        assert not (rec.get("is_observed") and rec.get("is_predicted")), f"Forbidden state on {rec}"
        if rec.get("price_source") == "unavailable":
            assert rec.get("modal_price") is None


def test_7_trends_official_only_filtering():
    """Verify trends endpoint only returns official sources."""
    res = client.get("/api/v1/prices/trends", params={
        "commodity": "Tomato",
        "market": "Madanapalli APMC",
        "days": 30
    })
    assert res.status_code == 200
    data = res.json()
    allowed = {"official_api", "official_database", "official_csv"}
    for pt in data:
        src = pt.get("price_source")
        if src:
            assert src in allowed


def test_8_weather_coverage_active_markets():
    """Verify weather coverage across active APMC markets."""
    res = client.get("/api/v1/weather/coverage")
    assert res.status_code == 200
    data = res.json()
    assert data["total_active_markets"] > 0
    assert data["markets_with_coordinates"] > 0
