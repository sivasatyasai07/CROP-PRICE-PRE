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
    commodity_id: int = Query(...),
    db: Session = Depends(get_db)
):
    # Subquery for latest date per market
    subq = db.query(
        CleanedMarketPrice.market_id,
        func.max(CleanedMarketPrice.observation_date).label("max_date")
    ).filter(CleanedMarketPrice.commodity_id == commodity_id)\
     .group_by(CleanedMarketPrice.market_id).subquery()

    results = db.query(CleanedMarketPrice, Market)\
                .join(subq, (CleanedMarketPrice.market_id == subq.c.market_id) & (CleanedMarketPrice.observation_date == subq.c.max_date))\
                .join(Market, CleanedMarketPrice.market_id == Market.id)\
                .filter(CleanedMarketPrice.commodity_id == commodity_id)\
                .all()

    return [
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
            unit=p.unit
        )
        for p, m in results
    ]
