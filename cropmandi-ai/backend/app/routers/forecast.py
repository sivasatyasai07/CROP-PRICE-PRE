import logging
import uuid
import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Market, Commodity, Prediction, OfficialMarketPrice
from app.schemas.forecast import (
    VerifiedForecastRequest,
    VerifiedForecastResponse,
    ForecastHistoryItem,
    OfficialStatusResponse
)
from app.services.forecast_reconciliation_service import reconcile_verified_forecast
from app.services.master_data_service import find_exact_master_record
from app.services.official_market_sync_service import fetch_date_range_records

logger = logging.getLogger(__name__)

router = APIRouter(tags=["forecast"])


@router.post("/forecast/verified", response_model=VerifiedForecastResponse)
@router.post("/api/v1/forecast/verified", response_model=VerifiedForecastResponse)
def verified_forecast(req: VerifiedForecastRequest, db: Session = Depends(get_db)):
    """
    Executes live API verification & price precedence reconciliation with forecast versioning:
    1. Priority 1: Fresh official API data from data.gov.in
    2. Priority 2: Authoritative master-data.csv exact match
    3. Priority 3: Direct multi-horizon CatBoost ML predictions (versioned)
    4. Priority 4: Unavailable
    """
    try:
        return reconcile_verified_forecast(db, req)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error executing verified forecast: %s", exc)
        raise HTTPException(status_code=500, detail=f"Forecast reconciliation error: {str(exc)}")


@router.get("/forecast/history", response_model=List[ForecastHistoryItem])
@router.get("/api/v1/forecast/history", response_model=List[ForecastHistoryItem])
def get_forecast_history(
    commodity: str = Query(..., example="Tomato"),
    market: str = Query(..., example="Pattikonda APMC"),
    target_date: Optional[str] = Query(None, example="2026-08-18"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Returns stored versioned predictions for the specified commodity and market.
    """
    from app.utils.market_normalization import normalize_market_name, normalize_commodity_name
    norm_m = normalize_market_name(market)
    norm_c = normalize_commodity_name(commodity)

    market_obj = db.query(Market).filter(
        (Market.canonical_name == market) | (Market.canonical_name == norm_m) | (Market.original_name == market)
    ).first()
    commodity_obj = db.query(Commodity).filter(
        (Commodity.canonical_name == commodity) | (Commodity.canonical_name == norm_c) | (Commodity.original_name == commodity)
    ).first()

    if not market_obj or not commodity_obj:
        return []

    MIN_DATE = datetime.date(2021, 1, 1)

    query = db.query(Prediction).filter(
        Prediction.market_id == market_obj.id,
        Prediction.commodity_id == commodity_obj.id,
        Prediction.forecast_origin_date >= MIN_DATE
    )

    if target_date:
        try:
            t_dt = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()
            query = query.filter(Prediction.target_date == t_dt)
        except ValueError:
            pass

    records = query.order_by(Prediction.target_date.desc(), Prediction.generated_at.desc()).limit(limit).all()

    items = []
    for r in records:
        items.append(ForecastHistoryItem(
            id=r.id,
            commodity=commodity_obj.canonical_name,
            market=market_obj.canonical_name,
            forecast_origin_date=r.forecast_origin_date,
            target_date=r.target_date,
            horizon=r.horizon,
            predicted_modal_price=r.predicted_modal_price,
            lower_bound=r.lower_bound,
            upper_bound=r.upper_bound,
            price_source=r.price_source or "predicted",
            prediction_status=r.prediction_status or "active",
            model_version=r.model_version,
            feature_snapshot_id=r.feature_snapshot_id,
            generated_at=r.generated_at or r.created_at,
            superseded_by_official=bool(r.superseded_by_official)
        ))
    return items


@router.get("/forecast/official-status", response_model=OfficialStatusResponse)
@router.get("/api/v1/forecast/official-status", response_model=OfficialStatusResponse)
def get_official_status(
    commodity: str = Query(..., example="Tomato"),
    market: str = Query(..., example="Pattikonda APMC"),
    target_date: str = Query(..., example="2026-08-18"),
    db: Session = Depends(get_db)
):
    """
    Checks if an official observed price exists for the target date from live API or master data.
    """
    try:
        t_dt = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid target_date format. Use YYYY-MM-DD")

    # 1. Check live API
    api_records = fetch_date_range_records(db=db, commodity=commodity, market=market, start_date=t_dt, end_date=t_dt)
    api_found = t_dt in api_records
    obs_price = None

    if api_found:
        obs_price = float(api_records[t_dt]["modal_price"])
        return OfficialStatusResponse(
            commodity=commodity,
            market=market,
            target_date=t_dt,
            official_api_checked=True,
            official_record_found=True,
            master_data_checked=False,
            master_record_found=False,
            active_prediction_exists=False,
            final_source="official_api",
            observed_price=obs_price
        )

    # 2. Check master data
    csv_res = find_exact_master_record(commodity=commodity, market=market, target_date=t_dt)
    csv_found = csv_res.record is not None and csv_res.is_valid
    if csv_found and csv_res.record:
        obs_price = float(csv_res.record["modal_price"])
        return OfficialStatusResponse(
            commodity=commodity,
            market=market,
            target_date=t_dt,
            official_api_checked=True,
            official_record_found=False,
            master_data_checked=True,
            master_record_found=True,
            active_prediction_exists=False,
            final_source="official_csv",
            observed_price=obs_price
        )

    return OfficialStatusResponse(
        commodity=commodity,
        market=market,
        target_date=t_dt,
        official_api_checked=True,
        official_record_found=False,
        master_data_checked=True,
        master_record_found=False,
        active_prediction_exists=True,
        final_source="predicted",
        observed_price=None
    )


@router.get("/forecast/predictions/3-day")
@router.get("/api/v1/forecast/predictions/3-day")
@router.get("/api/v1/predictions/3-day")
def get_3day_predictions_legacy(
    commodity: str = Query(..., example="Tomato"),
    market: str = Query(..., example="Madanapalli APMC"),
    prediction_date: Optional[str] = Query(None, example="2026-08-17"),
    db: Session = Depends(get_db)
):
    try:
        p_date = datetime.datetime.strptime(prediction_date, "%Y-%m-%d").date() if prediction_date else datetime.date.today()
    except ValueError:
        p_date = datetime.date.today()

    req = VerifiedForecastRequest(
        commodity=commodity,
        market=market,
        selected_date=p_date,
        force_refresh=True,
        request_id=str(uuid.uuid4())
    )
    resp = reconcile_verified_forecast(db, req)

    legacy_predictions = []
    for idx, r in enumerate(resp.records):
        legacy_predictions.append({
            "horizon": idx + 1,
            "target_date": r.date.isoformat(),
            "predicted_modal_price": r.modal_price,
            "lower_bound": r.lower_bound or r.min_price,
            "upper_bound": r.upper_bound or r.max_price,
            "confidence_level": r.confidence_level,
            "is_actual": r.is_observed,
            "is_observed": r.is_observed,
            "is_predicted": r.is_predicted,
            "price_source": r.price_source,
            "data_status": r.data_status,
            "source_label": r.source_label,
            "verification_status": r.verification_status,
            "source_name": r.source_name,
            "lookup_trace": r.lookup_trace
        })

    return {
        "request_id": resp.request_id,
        "commodity": commodity,
        "market": market,
        "prediction_date": p_date.isoformat(),
        "latest_observed_date": resp.latest_observed_date,
        "latest_observed_price": resp.latest_observed_price,
        "predictions": legacy_predictions,
        "trend_direction": resp.trend_direction,
        "percentage_change_3d": resp.percentage_change_3d,
        "records": [r.model_dump() if hasattr(r, "model_dump") else r.dict() for r in resp.records],
        "summary": resp.summary,
        "warnings": resp.warnings
    }


@router.get("/data-source/status")
@router.get("/api/v1/data-source/status")
def get_data_source_status(db: Session = Depends(get_db)):
    """
    Diagnostic status endpoint reporting API configuration, synchronization state,
    and latest observation dates without exposing secrets.
    """
    from app.config import settings
    from app.services.scheduler_service import get_sync_status
    from app.models import CleanedMarketPrice

    sync_st = get_sync_status()
    api_key_present = bool(settings.DATA_GOV_API_KEY)

    latest_db_rec = db.query(CleanedMarketPrice).order_by(CleanedMarketPrice.observation_date.desc()).first()
    latest_db_date = latest_db_rec.observation_date.isoformat() if latest_db_rec and latest_db_rec.observation_date else None

    api_status = "available" if api_key_present else "api_not_enabled"
    if sync_st.get("error"):
        api_status = "unavailable"

    return {
        "api_configured": api_key_present,
        "api_status": api_status,
        "last_sync_started_at": str(sync_st.get("started_at")),
        "last_sync_completed_at": str(sync_st.get("completed_at")) if sync_st.get("completed_at") else None,
        "last_sync_status": sync_st.get("status", "idle"),
        "latest_api_observation_date": str(sync_st.get("latest_api_date")) if sync_st.get("latest_api_date") else None,
        "latest_database_observation_date": latest_db_date,
        "records_received": sync_st.get("records_received", 0),
        "records_accepted": sync_st.get("records_accepted", 0),
        "records_rejected": sync_st.get("records_rejected", 0),
        "records_upserted": sync_st.get("records_accepted", 0),
        "error": sync_st.get("error")
    }


@router.get("/data-source/health")
@router.get("/api/v1/data-source/health")
def get_data_source_health(
    state: Optional[str] = Query("Andhra Pradesh"),
    district: Optional[str] = Query(None),
    market: Optional[str] = Query("Madanapalli"),
    commodity: Optional[str] = Query("Tomato")
):
    """
    Health check diagnostic reporting status, record count, actual fields, and latest date without exposing secrets.
    """
    from app.services.official_market_service import get_api_health
    return get_api_health(
        state=state,
        district=district,
        market=market,
        commodity=commodity
    )


@router.get("/data-source/live-snapshot")
@router.get("/api/v1/data-source/live-snapshot")
def get_live_mandi_snapshot():
    """Returns the latest JSON payload fetched from data.gov.in during forecast generation."""
    from app.services.official_market_service import get_live_fetched_json
    data = get_live_fetched_json()
    return data or {"message": "No active live snapshot. Click Generate Forecast to fetch live data."}


@router.delete("/data-source/live-snapshot")
@router.delete("/api/v1/data-source/live-snapshot")
def clear_live_mandi_snapshot():
    """Clears the live fetched JSON snapshot buffer."""
    from app.services.official_market_service import clear_live_fetched_json
    clear_live_fetched_json()
    return {"message": "Live fetched JSON snapshot cleared successfully."}


