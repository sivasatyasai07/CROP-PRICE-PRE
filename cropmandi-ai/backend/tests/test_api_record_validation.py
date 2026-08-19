import pytest
from datetime import date
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.official_market_sync_service import normalize_api_record, validate_api_record

def test_api_record_validation():
    db = SessionLocal()
    try:
        # Test 1: Valid OGD record variant with capitalized keys
        raw_ogd = {
            "Market": "Madanapalle",
            "Commodity": "Tomato",
            "Arrival_Date": "16/08/2026",
            "Min_Price": "1500",
            "Modal_Price": "1800",
            "Max_Price": "2000",
            "Arrival_Quantity": "150"
        }

        norm = normalize_api_record(raw_ogd, db)
        assert norm is not None
        assert norm["canonical_commodity"] == "Tomato"
        assert norm["canonical_market"] == "Madanapalli APMC"
        assert norm["observation_date"] == date(2026, 8, 16)
        assert norm["modal_price"] == 1800.0

        is_valid, reason = validate_api_record(norm, requested_comm="Tomato", requested_mkt="Madanapalli APMC")
        assert is_valid is True

        # Test 2: Invalid price bound (min > modal)
        invalid_raw = dict(raw_ogd)
        invalid_raw["Min_Price"] = "2500"
        norm_invalid = normalize_api_record(invalid_raw, db)
        assert norm_invalid is not None
        is_valid2, reason2 = validate_api_record(norm_invalid, requested_comm="Tomato", requested_mkt="Madanapalli APMC")
        assert is_valid2 is False
        assert "min_price" in reason2

        # Test 3: Commodity mismatch
        is_valid3, reason3 = validate_api_record(norm, requested_comm="Potato", requested_mkt="Madanapalli APMC")
        assert is_valid3 is False
        assert "Commodity mismatch" in reason3

    finally:
        db.close()
