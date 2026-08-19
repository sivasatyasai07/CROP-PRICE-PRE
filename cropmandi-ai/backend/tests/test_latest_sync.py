import pytest
from unittest.mock import patch, MagicMock
from app.database import SessionLocal
from app.services.official_market_sync_service import sync_latest_market_data


def test_latest_sync_execution():
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
            report = sync_latest_market_data(db=db, lookback_days=1)
            assert report["status"] == "success"
            assert "records_accepted" in report
            assert "records_rejected" in report
    finally:
        db.close()
