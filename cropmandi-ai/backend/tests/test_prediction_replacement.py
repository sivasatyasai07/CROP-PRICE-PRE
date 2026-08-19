import pytest
from datetime import date, datetime
from app.database import SessionLocal
from app.models import Market, Commodity, Prediction, OfficialMarketPrice
from app.services.official_market_sync_service import replace_stale_prediction

def test_prediction_replacement():
    db = SessionLocal()
    try:
        mkt = db.query(Market).first()
        comm = db.query(Commodity).first()
        test_dt = date(2026, 8, 25)

        # 1. Create a dummy prediction record
        pred = Prediction(
            market_id=mkt.id,
            commodity_id=comm.id,
            prediction_date=date(2026, 8, 20),
            target_date=test_dt,
            horizon=3,
            predicted_modal_price=2150.0,
            lower_bound=1900.0,
            upper_bound=2400.0,
            prediction_status="predicted",
            superseded_by_official=False
        )
        db.add(pred)
        db.commit()
        db.refresh(pred)

        # 2. Trigger replacement when official data arrives
        replaced_count = replace_stale_prediction(db, mkt.id, comm.id, test_dt, official_rec_id=999)
        assert replaced_count >= 1

        db.refresh(pred)
        assert pred.prediction_status == "superseded_by_official"
        assert pred.superseded_by_official is True
        assert pred.official_record_id == 999

    finally:
        # Cleanup test prediction
        db.query(Prediction).filter(Prediction.id == pred.id).delete()
        db.commit()
        db.close()
