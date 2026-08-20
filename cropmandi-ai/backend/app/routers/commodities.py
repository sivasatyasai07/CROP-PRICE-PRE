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
    start_date_str = start_date.strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")

    all_commodities = db.query(Commodity).filter(Commodity.is_active == True).order_by(Commodity.canonical_name.asc()).all()
    if not all_commodities:
        from app.services.seed_service import seed_markets_and_commodities
        seed_markets_and_commodities(db)
        all_commodities = db.query(Commodity).filter(Commodity.is_active == True).order_by(Commodity.canonical_name.asc()).all()

    master_idx = load_master_data()

    # Fast single-pass tally from master data
    master_comm_counts = {}
    master_comm_latest = {}
    for (comm_key, mkt_key, d_str), rec in master_idx.items():
        if start_date_str <= d_str <= today_str:
            try:
                p_val = float(rec.get("modal_price", 0))
                if p_val > 0:
                    master_comm_counts[comm_key] = master_comm_counts.get(comm_key, 0) + 1
                    if comm_key not in master_comm_latest or d_str > master_comm_latest[comm_key]:
                        master_comm_latest[comm_key] = d_str
            except Exception:
                pass

    # DB records aggregation
    db_comm_counts = {}
    db_comm_latest = {}
    try:
        db_recs = db.query(OfficialMarketPrice).filter(
            OfficialMarketPrice.observation_date >= start_date,
            OfficialMarketPrice.observation_date <= today
        ).all()
        for r in db_recs:
            if float(r.modal_price) > 0:
                cid = r.commodity_id
                db_comm_counts[cid] = db_comm_counts.get(cid, 0) + 1
                d_val = r.observation_date if isinstance(r.observation_date, date) else datetime.strptime(str(r.observation_date), "%Y-%m-%d").date()
                if cid not in db_comm_latest or d_val > db_comm_latest[cid]:
                    db_comm_latest[cid] = d_val
    except Exception:
        pass

    results: List[RecentCommodityOut] = []

    for c in all_commodities:
        norm_c = normalize_commodity_name(c.canonical_name).lower()
        records_in_window = master_comm_counts.get(norm_c, 0) + db_comm_counts.get(c.id, 0)
        
        latest_date_dt = None
        if norm_c in master_comm_latest:
            latest_date_dt = datetime.strptime(master_comm_latest[norm_c], "%Y-%m-%d").date()
        if c.id in db_comm_latest:
            if latest_date_dt is None or db_comm_latest[c.id] > latest_date_dt:
                latest_date_dt = db_comm_latest[c.id]

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



