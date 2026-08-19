from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date
from app.database import get_db
from app.models import CleanedMarketPrice, Market, Commodity
from app.schemas.price import LatestPriceOut, PriceHistoryItem, PriceCompareItem

router = APIRouter(prefix="/api/v1/prices", tags=["Prices"])

@router.get("/latest", response_model=LatestPriceOut)
def get_latest_price(
    market_id: int = Query(...),
    commodity_id: int = Query(...),
    db: Session = Depends(get_db)
):
    rec = db.query(CleanedMarketPrice)\
            .filter(CleanedMarketPrice.market_id == market_id, CleanedMarketPrice.commodity_id == commodity_id)\
            .order_by(CleanedMarketPrice.observation_date.desc()).first()

    if not rec:
        raise HTTPException(status_code=404, detail="No price record found for given market and commodity")

    market = db.query(Market).get(market_id)
    commodity = db.query(Commodity).get(commodity_id)

    return LatestPriceOut(
        market_id=market.id,
        market_name=market.canonical_name,
        district=market.district,
        commodity_id=commodity.id,
        commodity_name=commodity.canonical_name,
        observation_date=rec.observation_date,
        modal_price=rec.modal_price,
        min_price=rec.min_price,
        max_price=rec.max_price,
        arrival_quantity=rec.arrival_quantity,
        unit=rec.unit or commodity.unit
    )

@router.get("/history", response_model=List[PriceHistoryItem])
def get_price_history(
    market_id: int = Query(...),
    commodity_id: int = Query(...),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    MIN_DATE_STR = "2021-01-01"
    effective_start = max(start_date, MIN_DATE_STR) if start_date else MIN_DATE_STR

    q = db.query(CleanedMarketPrice)\
          .filter(
              CleanedMarketPrice.market_id == market_id,
              CleanedMarketPrice.commodity_id == commodity_id,
              CleanedMarketPrice.observation_date >= effective_start
          )

    if end_date:
        q = q.filter(CleanedMarketPrice.observation_date <= end_date)

    recs = q.order_by(CleanedMarketPrice.observation_date.desc()).limit(limit).all()
    recs = sorted(recs, key=lambda r: r.observation_date)

    if not recs:
        # Fallback to master-data.csv
        from app.services.master_data_service import get_master_data_path, parse_csv_date
        from app.utils.market_normalization import normalize_market_name, normalize_commodity_name
        import os, pandas as pd

        m_obj = db.query(Market).get(market_id)
        c_obj = db.query(Commodity).get(commodity_id)
        csv_path = get_master_data_path()
        if m_obj and c_obj and os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                comm_col = [col for col in df.columns if 'commodity' in col.lower() and 'group' not in col.lower()][0]
                mkt_col = [col for col in df.columns if 'market' in col.lower()][0]
                date_col = [col for col in df.columns if 'date' in col.lower()][0]
                modal_col = [col for col in df.columns if 'modal' in col.lower() or 'price' in col.lower()][0]
                arr_col = [col for col in df.columns if 'arrival' in col.lower() or 'quantity' in col.lower()][0]

                target_m = normalize_market_name(m_obj.canonical_name).lower()
                target_c = normalize_commodity_name(c_obj.canonical_name).lower()

                sub = df[
                    (df[comm_col].astype(str).apply(normalize_commodity_name).str.lower() == target_c) &
                    (df[mkt_col].astype(str).apply(normalize_market_name).str.lower() == target_m)
                ]

                history_items = []
                for _, row in sub.iterrows():
                    d_parsed = parse_csv_date(str(row[date_col]))
                    if not d_parsed or d_parsed < effective_start:
                        continue
                    if end_date and d_parsed > end_date:
                        continue
                    try:
                        p_val = float(row[modal_col])
                    except Exception:
                        continue
                    if p_val <= 0:
                        continue
                    try:
                        arr_val = float(row[arr_col])
                    except Exception:
                        arr_val = 0.0

                    history_items.append(
                        PriceHistoryItem(
                            observation_date=d_parsed,
                            modal_price=p_val,
                            min_price=round(p_val * 0.95, 2),
                            max_price=round(p_val * 1.05, 2),
                            arrival_quantity=arr_val,
                            quality_status="verified_master"
                        )
                    )
                if history_items:
                    history_items.sort(key=lambda x: str(x.observation_date))
                    return history_items[-limit:]
            except Exception:
                pass

    return [
        PriceHistoryItem(
            observation_date=r.observation_date,
            modal_price=r.modal_price,
            min_price=r.min_price,
            max_price=r.max_price,
            arrival_quantity=r.arrival_quantity,
            quality_status=r.quality_status
        )
        for r in recs
    ]

@router.get("/compare", response_model=List[PriceCompareItem])
def compare_market_prices(
    commodity_id: Optional[int] = Query(None),
    commodity: Optional[str] = Query(None),
    target_date: Optional[str] = Query(None, alias="date"),
    state: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    force_refresh: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    # Resolve commodity
    comm_obj = None
    if commodity_id:
        comm_obj = db.query(Commodity).get(commodity_id)
    elif commodity:
        comm_obj = db.query(Commodity).filter(
            (Commodity.canonical_name.ilike(f"%{commodity}%")) | (Commodity.original_name.ilike(f"%{commodity}%"))
        ).first()

    if not comm_obj:
        comm_obj = db.query(Commodity).first()
        if not comm_obj:
            from app.services.seed_service import seed_markets_and_commodities
            seed_markets_and_commodities(db)
            comm_obj = db.query(Commodity).first()

    c_id = comm_obj.id if comm_obj else 1

    # Subquery for latest date per market
    subq = db.query(
        CleanedMarketPrice.market_id,
        func.max(CleanedMarketPrice.observation_date).label("max_date")
    ).filter(CleanedMarketPrice.commodity_id == c_id)

    if target_date:
        subq = subq.filter(CleanedMarketPrice.observation_date <= target_date)
    if start_date:
        subq = subq.filter(CleanedMarketPrice.observation_date >= start_date)
    if end_date:
        subq = subq.filter(CleanedMarketPrice.observation_date <= end_date)

    subq = subq.group_by(CleanedMarketPrice.market_id).subquery()

    q = db.query(CleanedMarketPrice, Market)\
          .join(subq, (CleanedMarketPrice.market_id == subq.c.market_id) & (CleanedMarketPrice.observation_date == subq.c.max_date))\
          .join(Market, CleanedMarketPrice.market_id == Market.id)\
          .filter(CleanedMarketPrice.commodity_id == c_id)

    if district:
        q = q.filter(Market.district.ilike(f"%{district}%"))
    if state:
        q = q.filter(Market.state.ilike(f"%{state}%"))

    results = q.all()

    if not results:
        # Fallback to master-data.csv
        from app.services.master_data_service import get_master_data_path, parse_csv_date
        from app.utils.market_normalization import normalize_market_name, normalize_commodity_name
        import os, pandas as pd

        csv_path = get_master_data_path()
        if os.path.exists(csv_path) and comm_obj:
            try:
                df = pd.read_csv(csv_path)
                comm_col = [col for col in df.columns if 'commodity' in col.lower() and 'group' not in col.lower()][0]
                mkt_col = [col for col in df.columns if 'market' in col.lower()][0]
                date_col = [col for col in df.columns if 'date' in col.lower()][0]
                modal_col = [col for col in df.columns if 'modal' in col.lower() or 'price' in col.lower()][0]
                arr_col = [col for col in df.columns if 'arrival' in col.lower() or 'quantity' in col.lower()][0]
                dist_col = [col for col in df.columns if 'district' in col.lower()][0] if any('district' in c.lower() for c in df.columns) else None

                target_c = normalize_commodity_name(comm_obj.canonical_name).lower()
                sub = df[df[comm_col].astype(str).apply(normalize_commodity_name).str.lower() == target_c]

                market_latest_map = {}
                for _, row in sub.iterrows():
                    d_parsed = parse_csv_date(str(row[date_col]))
                    if not d_parsed:
                        continue
                    if target_date and d_parsed > target_date:
                        continue
                    m_norm = normalize_market_name(str(row[mkt_col]))
                    try:
                        p_val = float(row[modal_col])
                    except Exception:
                        continue
                    if p_val <= 0:
                        continue

                    if m_norm not in market_latest_map or d_parsed > market_latest_map[m_norm]["date"]:
                        try:
                            arr_val = float(row[arr_col])
                        except Exception:
                            arr_val = 0.0
                        d_name = str(row[dist_col]) if dist_col else "Andhra Pradesh"

                        # Find matching Market in DB
                        m_db = db.query(Market).filter(
                            (Market.canonical_name == m_norm) | (Market.original_name == m_norm)
                        ).first()

                        market_latest_map[m_norm] = {
                            "market_id": m_db.id if m_db else 999,
                            "market_name": m_db.canonical_name if m_db else m_norm,
                            "district": m_db.district if m_db else d_name,
                            "latitude": m_db.latitude if m_db else 14.5,
                            "longitude": m_db.longitude if m_db else 78.5,
                            "date": d_parsed,
                            "modal_price": p_val,
                            "min_price": round(p_val * 0.95, 2),
                            "max_price": round(p_val * 1.05, 2),
                            "arrival_quantity": arr_val,
                            "unit": comm_obj.unit or "Rs./Quintal"
                        }

                compare_items = [
                    PriceCompareItem(
                        market_id=item["market_id"],
                        market_name=item["market_name"],
                        district=item["district"],
                        latitude=item["latitude"],
                        longitude=item["longitude"],
                        latest_date=item["date"],
                        latest_modal_price=item["modal_price"],
                        min_price=item["min_price"],
                        max_price=item["max_price"],
                        arrival_quantity=item["arrival_quantity"],
                        unit=item["unit"]
                    )
                    for item in market_latest_map.values()
                ]
                if compare_items:
                    return sorted(compare_items, key=lambda x: x.market_name)
            except Exception:
                pass

    items = [
        PriceCompareItem(
            market_id=m.id,
            market_name=m.canonical_name,
            district=m.district,
            latitude=m.latitude,
            longitude=m.longitude,
            latest_date=p.observation_date,
            latest_modal_price=p.modal_price,
            min_price=p.min_price,
            max_price=p.max_price,
            arrival_quantity=p.arrival_quantity,
            unit=p.unit or comm_obj.unit if comm_obj else "Rs./Quintal"
        )
        for p, m in results
    ]

    return items
