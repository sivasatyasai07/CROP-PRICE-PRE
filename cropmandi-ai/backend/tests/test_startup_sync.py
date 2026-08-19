import pytest
from unittest.mock import patch, MagicMock
from app.database import SessionLocal
from app.services.scheduler_service import run_sync_task, get_sync_status


def test_startup_sync_status():
    db = SessionLocal()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "records": [
            {
                "state": "Andhra Pradesh",
                "district": "Chittoor",
                "market": "Madanapalli",
                "commodity": "Tomato",
                "arrival_date": "14/08/2026",
                "modal_price": "2100",
                "min_price": "1800",
                "max_price": "2400",
                "arrivals": "120"
            }
        ]
    }

    try:
        with patch("requests.get", return_value=mock_response):
            run_sync_task(lookback_days=1)
            status = get_sync_status()
            assert status["status"] in ["success", "in_progress", "idle"]
            assert status["records_accepted"] >= 0
            assert status["error"] is None
    finally:
        db.close()
