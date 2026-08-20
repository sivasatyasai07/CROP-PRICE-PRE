from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta, datetime
from app.database import get_db
from app.models import Commodity, OfficialMarketPrice
from app.schemas.commodity import CommodityOut
from app.schemas.price import RecentCommodityOut
from app.services.master_data_service import load_master_data
from app.utils.market_normalization import normalize_commodity_name
from app.utils.date_service import get_ist_today

router = APIRouter(prefix="/api/v1/commodities", tags=["Commodities"])


@router.get("", response_model=List[CommodityOut])
def list_commodities(db: Session = Depends(get_db)):
    commodities = db.query(Commodity).filter(Commodity.is_active == True).order_by(Commodity.canonical_name.asc()).all()
    if not commodities:
        from app.services.seed_service import seed_markets_and_commodities
        seed_markets_and_commodities(db)
        commodities = db.query(Commodity).filter(Commodity.is_active == True).order_by(Commodity.canonical_name.asc()).all()
    return commodities


@router.get("/recent", response_model=List[RecentCommodityOut])
def list_recent_commodities(
    days: int = Query(30, ge=1, le=365),
    min_records: int = Query(3, ge=1),
    db: Session = Depends(get_db)
):
    if not isinstance(days, int) or days <= 0:
        days = 30
    if not isinstance(min_records, int) or min_records <= 0:
        min_records = 3

    today = get_ist_today()
    start_date = today - timedelta(days=days - 1)

    all_commodities = db.query(Commodity).filter(Commodity.is_active == True).order_by(Commodity.canonical_name.asc()).all()
    if not all_commodities:
        from app.services.seed_service import seed_markets_and_commodities
        seed_markets_and_commodities(db)
        all_commodities = db.query(Commodity).filter(Commodity.is_active == True).order_by(Commodity.canonical_name.asc()).all()

    master_idx = load_master_data()

    # Tally official records per commodity in the last N days
    results: List[RecentCommodityOut] = []

    for c in all_commodities:
        norm_c = normalize_commodity_name(c.canonical_name).lower()
        records_in_window = 0
        latest_date_dt: Optional[date] = None

        # 1. Check master index
        for (comm_key, mkt_key, d_str), rec in master_idx.items():
            if comm_key == norm_c:
                try:
                    d = datetime.strptime(d_str, "%Y-%m-%d").date()
                    if start_date <= d <= today:
                        p_val = float(rec.get("modal_price", 0))
                        if p_val > 0:
                            records_in_window += 1
                            if latest_date_dt is None or d > latest_date_dt:
                                latest_date_dt = d
                except Exception:
                    pass

        # 2. Check DB OfficialMarketPrice
        try:
            db_recs = db.query(OfficialMarketPrice).filter(
                OfficialMarketPrice.commodity_id == c.id,
                OfficialMarketPrice.observation_date >= start_date,
                OfficialMarketPrice.observation_date <= today
            ).all()
            for r in db_recs:
                if float(r.modal_price) > 0:
                    records_in_window += 1
                    if latest_date_dt is None or r.observation_date > latest_date_dt:
                        latest_date_dt = r.observation_date
        except Exception:
            pass

        if records_in_window >= min_records:
            age_days = (today - latest_date_dt).days if latest_date_dt else None
            status = "available" if records_in_window >= 5 else "limited"
            results.append(RecentCommodityOut(
                id=c.id,
                canonical_name=c.canonical_name,
                commodity_name=c.canonical_name,
                latest_official_observed_date=latest_date_dt.strftime("%Y-%m-%d") if latest_date_dt else None,
                record_count=records_in_window,
                availability_status=status,
                data_age_days=age_days
            ))

    return sorted(results, key=lambda x: x.record_count, reverse=True)


