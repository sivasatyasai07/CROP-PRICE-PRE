import pytest
import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.services.date_service import get_ist_today

client = TestClient(app)

def test_future_date_rejected():
    today = get_ist_today()
    future_date = today + datetime.timedelta(days=2)

    payload = {
        "commodity": "Tomato",
        "market": "Madanapalli APMC",
        "selected_date": future_date.isoformat(),
        "force_refresh": False
    }

    response = client.post("/api/v1/forecast/verified", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "FUTURE_DATE_NOT_ALLOWED"

def test_today_date_accepted():
    today = get_ist_today()

    payload = {
        "commodity": "Tomato",
        "market": "Madanapalli APMC",
        "selected_date": today.isoformat(),
        "force_refresh": False
    }

    response = client.post("/api/v1/forecast/verified", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["selected_date"] == today.isoformat()
    assert len(data["records"]) == 4

    # The subsequent dates (today+1, today+2, today+3) must be marked as predicted and never as official
    for r in data["records"]:
        r_date = datetime.date.fromisoformat(r["date"])
        if r_date > today:
            assert r["is_observed"] is False
            assert r["price_source"] in ["predicted", "unavailable"]

def test_past_date_accepted():
    today = get_ist_today()
    past_date = today - datetime.timedelta(days=5)

    payload = {
        "commodity": "Tomato",
        "market": "Madanapalli APMC",
        "selected_date": past_date.isoformat(),
        "force_refresh": False
    }

    response = client.post("/api/v1/forecast/verified", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["selected_date"] == past_date.isoformat()
    assert len(data["records"]) == 4
