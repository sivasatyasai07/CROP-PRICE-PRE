import os
import uuid
import datetime
import logging
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models import CleanedMarketPrice, OfficialMarketPrice, Market, Commodity
from app.models.prediction import Prediction
from app.schemas.forecast import (
    VerifiedForecastRequest,
    VerifiedForecastResponse,
    ForecastRecord,
    DateRangeSummary,
    LookupTraceStep
)
from app.services.master_data_service import find_exact_master_record
from app.services.official_market_sync_service import (
    fetch_date_range_records,
    refresh_before_forecast,
    get_latest_official_date
)
from app.ml.predict import generate_3day_prediction
from app.ml.dataset_builder import build_dataset_from_db
from app.config import settings
from app.services.date_service import get_ist_today, parse_date_safely

logger = logging.getLogger(__name__)

OFFICIAL_API_SOURCE_LABEL = "Official value from data.gov.in"
OFFICIAL_CSV_SOURCE_LABEL = "Official value from master-data.csv"
PREDICTED_MODEL_SOURCE_LABEL = "Predicted by trained CatBoost model"
FALLBACK_LAST_OBSERVED_SOURCE_LABEL = "Fallback estimate: last observed official price"
FALLBACK_ROLLING_AVERAGE_SOURCE_LABEL = "Fallback estimate: historical rolling-average estimate"
UNAVAILABLE_SOURCE_LABEL = "Data unavailable"


def get_date_sequence(start_date: datetime.date, num_days: int = 4) -> List[datetime.date]:
    return [start_date + datetime.timedelta(days=i) for i in range(num_days)]


def supersede_stale_predictions_for_date(db: Session, market_id: int, commodity_id: int, target_date: datetime.date):
    """Marks stored predictions for this target date as superseded by official data."""
    try:
        preds = db.query(Prediction).filter(
            Prediction.market_id == market_id,
            Prediction.commodity_id == commodity_id,
            Prediction.target_date == target_date,
            Prediction.prediction_status != "superseded_by_official"
        ).all()
        for p in preds:
            p.prediction_status = "superseded_by_official"
            p.superseded_by_official = True
        if preds:
            db.commit()
    except Exception as exc:
        db.rollback()
        logger.warning("Could not supersede predictions for date %s: %s", target_date, exc)


def record_prediction_versioning(
    db: Session,
    market_id: int,
    commodity_id: int,
    forecast_origin_date: datetime.date,
    target_date: datetime.date,
    horizon: int,
    predicted_modal_price: float,
    lower_bound: Optional[float],
    upper_bound: Optional[float],
    model_version: str,
    feature_snapshot_id: str,
    price_source: str = "predicted_model",
    prediction_method: str = "trained_model"
) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Saves a versioned prediction row. If a previous active prediction existed for this target date
    from an older origin, marks it superseded_by_newer_forecast and returns its summary.
    """
    previous_forecast = None
    try:
        existing_active = db.query(Prediction).filter(
            Prediction.market_id == market_id,
            Prediction.commodity_id == commodity_id,
            Prediction.target_date == target_date,
            Prediction.prediction_status == "active"
        ).first()

        if existing_active:
            if existing_active.forecast_origin_date != forecast_origin_date:
                previous_forecast = {
                    "forecast_origin_date": existing_active.forecast_origin_date.isoformat(),
                    "predicted_modal_price": existing_active.predicted_modal_price,
                    "model_version": existing_active.model_version
                }
                existing_active.prediction_status = "superseded_by_newer_forecast"
            else:
                # Same origin date and target date already generated
                return "active", None

        new_pred = Prediction(
            market_id=market_id,
            commodity_id=commodity_id,
            prediction_date=forecast_origin_date,
            forecast_origin_date=forecast_origin_date,
            target_date=target_date,
            horizon=horizon,
            predicted_modal_price=predicted_modal_price,
            lower_bound=lower_bound or predicted_modal_price,
            upper_bound=upper_bound or predicted_modal_price,
            price_source=price_source,
            prediction_status="active",
            model_version=model_version,
            feature_snapshot_id=feature_snapshot_id,
            generated_at=datetime.datetime.utcnow()
        )
        db.add(new_pred)
        db.commit()
        db.refresh(new_pred)
        return "active", previous_forecast
    except Exception as exc:
        db.rollback()
        logger.warning("Could not persist versioned prediction: %s", exc)
        return "active", previous_forecast


def resolve_price_for_date(
    commodity: str,
    market: str,
    target_date: datetime.date,
    forecast_origin_date: datetime.date,
    market_obj: Market,
    commodity_obj: Commodity,
    db: Session,
    official_api_map: Dict[datetime.date, Dict[str, Any]],
    predictions_map: Dict[str, Dict[str, Any]],
    api_searched: bool,
    now: datetime.datetime,
    feature_snapshot_id: str,
    model_version: str,
    district: Optional[str] = None,
    state: Optional[str] = None,
    latest_recorded_price: Optional[float] = None,
    latest_recorded_date: Optional[str] = None
) -> ForecastRecord:
    trace: List[Dict[str, Any]] = []
    horizon = (target_date - forecast_origin_date).days

    # 1. SOURCE 1: Fresh Official API Check
    api_record = official_api_map.get(target_date)
    
    # If not in rolling map, perform explicit dynamic date lookup if today or past
    today_ist = get_ist_today()
    if not api_record and target_date <= today_ist and api_searched:
        from app.services.official_market_service import fetch_exact_official_record
        exact_rec, api_step = fetch_exact_official_record(
            db=db,
            commodity=commodity,
            market=market,
            target_date=target_date,
            district=district,
            state=state
        )
        if exact_rec:
            api_record = exact_rec
            official_api_map[target_date] = exact_rec

    api_found = api_record is not None

    trace.append({
        "source": "official_api",
        "searched": api_searched and target_date <= today_ist,
        "found": api_found,
        "status": "exact_record_found" if api_found else ("future_date_not_in_api" if target_date > today_ist else "no_exact_record")
    })

    if api_found and api_record:
        modal_p = round(float(api_record["modal_price"]), 2)
        min_p = round(float(api_record["min_price"]), 2) if api_record.get("min_price") is not None else None
        max_p = round(float(api_record["max_price"]), 2) if api_record.get("max_price") is not None else None
        arr_q = round(float(api_record["arrival_quantity"]), 2) if api_record.get("arrival_quantity") is not None else None

        supersede_stale_predictions_for_date(db, market_obj.id, commodity_obj.id, target_date)

        trace.append({
            "source": "master-data.csv",
            "searched": False,
            "found": False,
            "status": "not_needed"
        })
        trace.append({
            "source": "prediction",
            "searched": False,
            "found": False,
            "status": "not_needed"
        })

        return ForecastRecord(
            date=target_date,
            target_date=target_date,
            forecast_origin_date=forecast_origin_date,
            horizon=horizon,
            modal_price=modal_p,
            min_price=min_p,
            max_price=max_p,
            arrival_quantity=arr_q,
            arrival_unit=api_record.get("arrival_unit", "Metric Tonnes"),
            price_unit=api_record.get("price_unit", "Rs./Quintal"),
            price_source="official_api",
            data_status="observed_live",
            prediction_status="superseded_by_official",
            prediction_method="official_observation",
            model_predict_called=False,
            prediction_executed=False,
            model_error_code=None,
            raw_model_output=None,
            final_prediction=None,
            is_observed=True,
            is_predicted=False,
            source_label=OFFICIAL_API_SOURCE_LABEL,
            verification_status="api_live_verified",
            source_name="Official value from data.gov.in",
            source_record_id=str(api_record.get("record_id", "")) if api_record.get("record_id") else None,
            fetched_at=now,
            data_fetched_at=now,
            generated_at=None,
            model_name=None,
            model_version=None,
            data_freshness="live_api",
            confidence_level=None,
            confidence_source="unavailable",
            interval_available=False,
            interval_method=None,
            lower_bound=None,
            upper_bound=None,
            fallback_reason=None,
            arrival_features_used=False,
            weather_features_used=False,
            seasonal_features_used=False,
            api_checked=True,
            api_record_found=True,
            master_csv_checked=False,
            master_csv_record_found=False,
            prediction_generated=False,
            final_source="official_api",
            lookup_trace=trace
        )

    # 2. SOURCE 2: Authoritative master-data.csv Check
    csv_result = find_exact_master_record(
        commodity=commodity,
        market=market,
        target_date=target_date,
        state=state,
        district=district
    )
    csv_found = csv_result.record is not None and csv_result.is_valid

    trace.append({
        "source": "master-data.csv",
        "searched": True,
        "found": csv_found,
        "status": "record_found" if csv_found else "record_not_found"
    })

    if csv_found and csv_result.record:
        rec = csv_result.record
        modal_p = round(float(rec["modal_price"]), 2)
        arr_q = round(float(rec["arrival_quantity"]), 2) if rec.get("arrival_quantity") is not None else None

        supersede_stale_predictions_for_date(db, market_obj.id, commodity_obj.id, target_date)

        return ForecastRecord(
            date=target_date,
            target_date=target_date,
            forecast_origin_date=forecast_origin_date,
            horizon=horizon,
            modal_price=modal_p,
            min_price=None,
            max_price=None,
            arrival_quantity=arr_q,
            arrival_unit=rec.get("arrival_unit", "Metric Tonnes"),
            price_unit=rec.get("price_unit", "Rs./Quintal"),
            price_source="official_csv",
            data_status="observed_csv",
            prediction_status="superseded_by_official",
            prediction_method="official_observation",
            model_predict_called=False,
            prediction_executed=False,
            model_error_code=None,
            raw_model_output=None,
            final_prediction=None,
            is_observed=True,
            is_predicted=False,
            source_label=OFFICIAL_CSV_SOURCE_LABEL,
            verification_status="master_csv_verified",
            source_name="Official value from master-data.csv",
            source_record_id=None,
            fetched_at=None,
            data_fetched_at=None,
            generated_at=None,
            model_name=None,
            model_version=None,
            data_freshness="historical_master",
            confidence_level=None,
            confidence_source="unavailable",
            interval_available=False,
            interval_method=None,
            lower_bound=None,
            upper_bound=None,
            fallback_reason=None,
            arrival_features_used=False,
            weather_features_used=False,
            seasonal_features_used=False,
            api_checked=True,
            api_record_found=False,
            master_csv_checked=True,
            master_csv_record_found=True,
            prediction_generated=False,
            final_source="official_csv",
            lookup_trace=trace
        )

    # 3. SOURCE 3: Authoritative Database Official & Cleaned Records Check
    db_obs = db.query(OfficialMarketPrice).filter(
        OfficialMarketPrice.market_id == market_obj.id,
        OfficialMarketPrice.commodity_id == commodity_obj.id,
        OfficialMarketPrice.observation_date == target_date
    ).first()
    if not db_obs:
        db_obs = db.query(CleanedMarketPrice).filter(
            CleanedMarketPrice.market_id == market_obj.id,
            CleanedMarketPrice.commodity_id == commodity_obj.id,
            CleanedMarketPrice.observation_date == target_date
        ).first()

    if db_obs and db_obs.modal_price and float(db_obs.modal_price) > 0:
        modal_p = round(float(db_obs.modal_price), 2)
        min_p = round(float(getattr(db_obs, "min_price", None)), 2) if getattr(db_obs, "min_price", None) is not None else None
        max_p = round(float(getattr(db_obs, "max_price", None)), 2) if getattr(db_obs, "max_price", None) is not None else None
        arr_q = round(float(getattr(db_obs, "arrival_quantity", None)), 2) if getattr(db_obs, "arrival_quantity", None) is not None else None

        supersede_stale_predictions_for_date(db, market_obj.id, commodity_obj.id, target_date)

        trace.append({
            "source": "official_database",
            "searched": True,
            "found": True,
            "status": "exact_record_found",
            "reason": f"Official recorded price for {target_date} found in verified database."
        })

        return ForecastRecord(
            date=target_date,
            target_date=target_date,
            forecast_origin_date=forecast_origin_date,
            horizon=horizon,
            modal_price=modal_p,
            min_price=min_p,
            max_price=max_p,
            arrival_quantity=arr_q,
            arrival_unit="Metric Tonnes",
            price_unit="Rs./Quintal",
            price_source="official_database",
            data_status="observed_database",
            prediction_status="superseded_by_official",
            prediction_method="official_observation",
            model_predict_called=False,
            prediction_executed=False,
            model_error_code=None,
            raw_model_output=None,
            final_prediction=None,
            is_observed=True,
            is_predicted=False,
            source_label="Official value from database",
            verification_status="db_verified",
            source_name="Official observed price from database",
            source_record_id=None,
            fetched_at=now,
            data_fetched_at=now,
            generated_at=None,
            model_name=None,
            model_version=None,
            data_freshness="database_official",
            confidence_level=None,
            confidence_source="unavailable",
            interval_available=False,
            interval_method=None,
            lower_bound=None,
            upper_bound=None,
            fallback_reason=None,
            arrival_features_used=False,
            weather_features_used=False,
            seasonal_features_used=False,
            api_checked=True,
            api_record_found=False,
            master_csv_checked=True,
            master_csv_record_found=False,
            prediction_generated=False,
            final_source="official_database",
            lookup_trace=trace
        )

    # 4. SOURCE 4: CatBoost ML Prediction Candidate
    pred_data = predictions_map.get(target_date.isoformat())
    if pred_data:
        p_src = pred_data.get("price_source", "unavailable")
        p_meth = pred_data.get("prediction_method", "none")
        p_exec = bool(pred_data.get("prediction_executed", False))
        p_called = bool(pred_data.get("model_predict_called", False))
        pred_p = pred_data.get("predicted_modal_price")
        low_b = pred_data.get("lower_bound")
        up_b = pred_data.get("upper_bound")
        conf_lvl = pred_data.get("confidence_level")
        conf_src = pred_data.get("confidence_source", "unavailable")
        interval_avail = bool(pred_data.get("interval_available", False))
        interval_meth = pred_data.get("interval_method")
        m_version = pred_data.get("model_version", model_version)
        m_name = pred_data.get("model_name")
        snap_id = pred_data.get("feature_snapshot_id", feature_snapshot_id)
        fb_reason = pred_data.get("fallback_reason")
        m_err = pred_data.get("model_error_code")
        raw_out = pred_data.get("raw_model_output")
        final_p = pred_data.get("final_prediction", pred_p)
        arr_used = bool(pred_data.get("arrival_features_used", False))
        wth_used = bool(pred_data.get("weather_features_used", False))
        sea_used = bool(pred_data.get("seasonal_features_used", False))
        arr_miss = pred_data.get("arrival_missing")
        wth_miss = pred_data.get("weather_missing")
        feat_date = pred_data.get("feature_row_date")

        if p_src == "predicted_model" and p_exec and pred_p is not None:
            status_label, prev_forecast = record_prediction_versioning(
                db=db,
                market_id=market_obj.id,
                commodity_id=commodity_obj.id,
                forecast_origin_date=forecast_origin_date,
                target_date=target_date,
                horizon=horizon,
                predicted_modal_price=pred_p,
                lower_bound=low_b or pred_p,
                upper_bound=up_b or pred_p,
                model_version=m_version,
                feature_snapshot_id=snap_id,
                price_source="predicted_model",
                prediction_method="trained_model"
            )

            trace.append({
                "source": "predicted_model",
                "searched": True,
                "found": True,
                "status": "generated",
                "reason": "Value predicted by trained CatBoost model."
            })

            return ForecastRecord(
                date=target_date,
                target_date=target_date,
                forecast_origin_date=forecast_origin_date,
                horizon=horizon,
                modal_price=pred_p,
                min_price=low_b,
                max_price=up_b,
                arrival_quantity=None,
                arrival_unit="Metric Tonnes",
                price_unit="Rs./Quintal",
                price_source="predicted_model",
                data_status="predicted_model",
                prediction_status=status_label,
                prediction_method="trained_model",
                model_predict_called=True,
                prediction_executed=True,
                model_error_code=None,
                raw_model_output=raw_out,
                final_prediction=final_p,
                is_observed=False,
                is_predicted=True,
                source_label=PREDICTED_MODEL_SOURCE_LABEL,
                verification_status="prediction_generated",
                source_name=m_name or "CatBoost Direct Horizon Model",
                source_record_id=None,
                fetched_at=now,
                data_fetched_at=None,
                generated_at=now,
                model_name=m_name or "CatBoost Direct Horizon Model",
                model_version=m_version,
                feature_snapshot_id=snap_id,
                previous_forecast=prev_forecast,
                data_freshness="predicted",
                confidence_level=conf_lvl,
                confidence_source=conf_src,
                interval_available=interval_avail,
                interval_method=interval_meth,
                lower_bound=low_b,
                upper_bound=up_b,
                confidence_interval={"lower": low_b, "upper": up_b} if low_b and up_b else None,
                fallback_reason=None,
                arrival_features_used=arr_used,
                weather_features_used=wth_used,
                seasonal_features_used=sea_used,
                arrival_missing=arr_miss,
                weather_missing=wth_miss,
                feature_row_date=feat_date,
                api_checked=True,
                api_record_found=False,
                master_csv_checked=True,
                master_csv_record_found=False,
                prediction_generated=True,
                final_source="predicted_model",
                lookup_trace=trace
            )

        elif p_src == "fallback_last_observed" and pred_p is not None:
            status_label, prev_forecast = record_prediction_versioning(
                db=db,
                market_id=market_obj.id,
                commodity_id=commodity_obj.id,
                forecast_origin_date=forecast_origin_date,
                target_date=target_date,
                horizon=horizon,
                predicted_modal_price=pred_p,
                lower_bound=low_b or pred_p,
                upper_bound=up_b or pred_p,
                model_version="fallback-baseline",
                feature_snapshot_id=snap_id,
                price_source="fallback_last_observed",
                prediction_method="fallback"
            )

            trace.append({
                "source": "fallback_last_observed",
                "searched": True,
                "found": True,
                "status": "fallback_applied",
                "reason": fb_reason or "Official value was not available. Fallback estimate from last observed price applied."
            })

            return ForecastRecord(
                date=target_date,
                target_date=target_date,
                forecast_origin_date=forecast_origin_date,
                horizon=horizon,
                modal_price=pred_p,
                min_price=None,
                max_price=None,
                arrival_quantity=None,
                arrival_unit="Metric Tonnes",
                price_unit="Rs./Quintal",
                price_source="fallback_last_observed",
                data_status="predicted_fallback",
                prediction_status=status_label,
                prediction_method="fallback",
                model_predict_called=p_called,
                prediction_executed=False,
                model_error_code=m_err,
                raw_model_output=None,
                final_prediction=pred_p,
                is_observed=False,
                is_predicted=True,
                source_label=FALLBACK_LAST_OBSERVED_SOURCE_LABEL,
                verification_status="fallback_applied",
                source_name=m_name or "Last observed price fallback",
                source_record_id=None,
                fetched_at=now,
                data_fetched_at=None,
                generated_at=now,
                model_name=m_name or "Last observed price fallback",
                model_version="fallback-baseline",
                feature_snapshot_id=snap_id,
                previous_forecast=prev_forecast,
                data_freshness="fallback",
                confidence_level=None,
                confidence_source="unavailable",
                interval_available=False,
                interval_method=None,
                lower_bound=None,
                upper_bound=None,
                confidence_interval=None,
                fallback_reason=fb_reason or "Official data unavailable and model prediction failed.",
                arrival_features_used=False,
                weather_features_used=False,
                seasonal_features_used=False,
                arrival_missing=True,
                weather_missing=True,
                feature_row_date=feat_date,
                api_checked=True,
                api_record_found=False,
                master_csv_checked=True,
                master_csv_record_found=False,
                prediction_generated=True,
                final_source="fallback_last_observed",
                lookup_trace=trace
            )

    # 4. SOURCE 4: Latest Recorded Price Fallback (if exact date is not yet published)
    if latest_recorded_price is not None and latest_recorded_price > 0:
        rec_label = f"Last Recorded Price ({latest_recorded_date})" if latest_recorded_date else "Last Recorded Official Price"
        trace.append({
            "source": "fallback_last_observed",
            "searched": True,
            "found": True,
            "status": "latest_recorded_applied",
            "reason": f"Exact record for {target_date} not yet published. Showing latest recorded official price ({latest_recorded_date or 'recent history'})."
        })

        return ForecastRecord(
            date=target_date,
            target_date=target_date,
            forecast_origin_date=forecast_origin_date,
            horizon=horizon,
            modal_price=round(float(latest_recorded_price), 2),
            min_price=None,
            max_price=None,
            arrival_quantity=None,
            arrival_unit="Metric Tonnes",
            price_unit="Rs./Quintal",
            price_source="fallback_last_observed",
            data_status="observed_historical",
            prediction_status="last_recorded",
            prediction_method="last_recorded",
            model_predict_called=False,
            prediction_executed=False,
            model_error_code=None,
            raw_model_output=None,
            final_prediction=round(float(latest_recorded_price), 2),
            is_observed=True,
            is_predicted=False,
            source_label=rec_label,
            verification_status="last_recorded_verified",
            source_name=f"Latest recorded price (as of {latest_recorded_date or 'recent history'})",
            source_record_id=None,
            fetched_at=None,
            data_fetched_at=None,
            generated_at=now,
            model_name="Latest recorded baseline",
            model_version=None,
            feature_snapshot_id=feature_snapshot_id,
            previous_forecast=None,
            data_freshness="historical_latest",
            confidence_level=None,
            confidence_source="unavailable",
            interval_available=False,
            interval_method=None,
            lower_bound=None,
            upper_bound=None,
            confidence_interval=None,
            fallback_reason=f"Official data for {target_date} not yet published. Showing latest recorded price from {latest_recorded_date}.",
            arrival_features_used=False,
            weather_features_used=False,
            seasonal_features_used=False,
            arrival_missing=True,
            weather_missing=True,
            feature_row_date=latest_recorded_date,
            api_checked=True,
            api_record_found=False,
            master_csv_checked=True,
            master_csv_record_found=False,
            prediction_generated=False,
            final_source="fallback_last_observed",
            lookup_trace=trace
        )

    # 5. SOURCE 5: Unavailable
    trace.append({
        "source": "unavailable",
        "searched": True,
        "found": False,
        "status": "unavailable",
        "reason": "No official data or valid prediction could be determined."
    })

    return ForecastRecord(
        date=target_date,
        target_date=target_date,
        forecast_origin_date=forecast_origin_date,
        horizon=horizon,
        modal_price=None,
        min_price=None,
        max_price=None,
        arrival_quantity=None,
        arrival_unit="Metric Tonnes",
        price_unit="Rs./Quintal",
        price_source="unavailable",
        data_status="unavailable",
        prediction_status="unavailable",
        prediction_method="none",
        model_predict_called=False,
        prediction_executed=False,
        model_error_code=None,
        raw_model_output=None,
        final_prediction=None,
        is_observed=False,
        is_predicted=False,
        source_label=UNAVAILABLE_SOURCE_LABEL,
        verification_status="unavailable",
        source_name=None,
        source_record_id=None,
        fetched_at=None,
        data_fetched_at=None,
        generated_at=None,
        model_name=None,
        model_version=None,
        data_freshness="unavailable",
        confidence_level=None,
        confidence_source="unavailable",
        interval_available=False,
        interval_method=None,
        lower_bound=None,
        upper_bound=None,
        confidence_interval=None,
        fallback_reason="No official data or valid prediction could be determined.",
        arrival_features_used=False,
        weather_features_used=False,
        seasonal_features_used=False,
        arrival_missing=True,
        weather_missing=True,
        feature_row_date=None,
        api_checked=True,
        api_record_found=False,
        master_csv_checked=True,
        master_csv_record_found=False,
        prediction_generated=False,
        final_source="unavailable",
        lookup_trace=trace
    )


def reconcile_verified_forecast(db: Session, req: VerifiedForecastRequest) -> VerifiedForecastResponse:
    from fastapi import HTTPException
    from app.services.official_market_service import clear_live_fetched_json, save_live_fetched_json
    clear_live_fetched_json()
    now = datetime.datetime.utcnow()
    req_id = req.request_id or str(uuid.uuid4())
    today_ist = get_ist_today()

    MIN_ALLOWED_DATE = datetime.date(2021, 1, 1)

    if req.selected_date < MIN_ALLOWED_DATE:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "DATE_TOO_EARLY",
                "message": f"Selected date ({req.selected_date}) is before the minimum supported date (01-01-2021). Forecast data is available only from 01-01-2021 onwards."
            }
        )

    if req.selected_date > today_ist:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "FUTURE_DATE_NOT_ALLOWED",
                "message": f"Selected date ({req.selected_date}) cannot be in the future. Today in IST is {today_ist}."
            }
        )

    from app.utils.market_normalization import normalize_market_name, normalize_commodity_name
    norm_market = normalize_market_name(req.market)
    norm_comm = normalize_commodity_name(req.commodity)

    market_obj = db.query(Market).filter(
        (Market.canonical_name == req.market) |
        (Market.original_name == req.market) |
        (Market.canonical_name == norm_market) |
        (Market.original_name == norm_market)
    ).first()

    if not market_obj:
        market_obj = Market(
            canonical_name=norm_market,
            original_name=req.market,
            district="Andhra Pradesh",
            state="Andhra Pradesh",
            is_active=True
        )
        db.add(market_obj)
        db.commit()
        db.refresh(market_obj)

    commodity_obj = db.query(Commodity).filter(
        (Commodity.canonical_name == req.commodity) |
        (Commodity.original_name == req.commodity) |
        (Commodity.canonical_name == norm_comm) |
        (Commodity.original_name == norm_comm)
    ).first()

    if not commodity_obj:
        commodity_obj = Commodity(
            canonical_name=norm_comm,
            original_name=req.commodity,
            commodity_group="General",
            unit="Rs./Quintal"
        )
        db.add(commodity_obj)
        db.commit()
        db.refresh(commodity_obj)

    # 4-date forecast sequence [selected_date, selected_date+1, selected_date+2, selected_date+3]
    forecast_dates = get_date_sequence(req.selected_date, 4)
    start_date, end_date = forecast_dates[0], forecast_dates[-1]

    # Step 1: Pre-fetch latest official API data across rolling lookback window through today
    sync_summary = refresh_before_forecast(
        db=db,
        commodity=req.commodity,
        market=req.market,
        lookback_days=settings.LIVE_REFRESH_LOOKBACK_DAYS,
        force_refresh=req.force_refresh
    )
    db.commit()

    official_api_map: Dict[datetime.date, Dict[str, Any]] = sync_summary.get("records_by_date", {})
    api_status = sync_summary.get("api_status", "checked_no_records")
    api_checked = sync_summary.get("api_called", True)

    # Step 2: Dynamically rebuild fresh feature dataset containing all newly inserted/updated records
    fresh_df = build_dataset_from_db(db)

    # ML Predictions candidate map for dates lacking official data
    predictions_map: Dict[str, Dict[str, Any]] = {}
    feature_snapshot_id = f"snap_{req.commodity}_{req.market}_{req.selected_date.strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"
    model_ver = "catboost-v2.1"
    feature_explanations: List[str] = []
    feature_schema_match = True
    missing_feats: List[str] = []
    unexpected_feats: List[str] = []
    exp_feat_cnt: Optional[int] = None
    run_feat_cnt: Optional[int] = None
    feature_latest_date = None
    latest_price_used = None
    latest_arrival_used = None
    prediction_service_status = "success"
    prediction_error_code: Optional[str] = None
    prediction_error_message: Optional[str] = None

    try:
        pred_resp = generate_3day_prediction(
            db=db,
            commodity_name=commodity_obj.canonical_name,
            market_name=market_obj.canonical_name,
            prediction_date_str=req.selected_date.isoformat(),
            df_all=fresh_df
        )
        pred_list = pred_resp.get("predictions", []) if isinstance(pred_resp, dict) else getattr(pred_resp, "predictions", [])
        model_ver = pred_resp.get("model_version", model_ver)
        feature_snapshot_id = pred_resp.get("feature_snapshot_id", feature_snapshot_id)
        feature_explanations = pred_resp.get("feature_explanations", [])
        feature_schema_match = bool(pred_resp.get("feature_schema_match", True))
        missing_feats = pred_resp.get("missing_features", [])
        unexpected_feats = pred_resp.get("unexpected_features", [])
        exp_feat_cnt = pred_resp.get("expected_feature_count")
        run_feat_cnt = pred_resp.get("runtime_feature_count")
        feature_latest_date = pred_resp.get("feature_latest_date")
        latest_price_used = pred_resp.get("latest_price_used_for_features")
        latest_arrival_used = pred_resp.get("latest_arrival_used_for_features")

        # Determine prediction service status
        if any(p.get("price_source") in ["fallback_last_observed", "unavailable"] for p in pred_list if isinstance(p, dict)):
            prediction_service_status = "fallback"

        for p in pred_list:
            t_date = p.get("target_date") if isinstance(p, dict) else getattr(p, "target_date", None)
            if t_date:
                predictions_map[str(t_date)] = p if isinstance(p, dict) else {
                    "predicted_modal_price": getattr(p, "predicted_modal_price", None),
                    "lower_bound": getattr(p, "lower_bound", None),
                    "upper_bound": getattr(p, "upper_bound", None),
                    "confidence_level": getattr(p, "confidence_level", None),
                    "confidence_source": getattr(p, "confidence_source", "unavailable"),
                    "interval_available": getattr(p, "interval_available", False),
                    "interval_method": getattr(p, "interval_method", None),
                    "price_source": getattr(p, "price_source", "unavailable"),
                    "prediction_method": getattr(p, "prediction_method", "none"),
                    "prediction_executed": getattr(p, "prediction_executed", False),
                    "model_predict_called": getattr(p, "model_predict_called", False),
                    "model_error_code": getattr(p, "model_error_code", None),
                    "raw_model_output": getattr(p, "raw_model_output", None),
                    "final_prediction": getattr(p, "final_prediction", None),
                    "model_name": getattr(p, "model_name", None),
                    "model_version": getattr(p, "model_version", model_ver),
                    "feature_snapshot_id": getattr(p, "feature_snapshot_id", feature_snapshot_id),
                    "fallback_reason": getattr(p, "fallback_reason", None),
                    "arrival_features_used": getattr(p, "arrival_features_used", False),
                    "weather_features_used": getattr(p, "weather_features_used", False),
                    "seasonal_features_used": getattr(p, "seasonal_features_used", False),
                    "arrival_missing": getattr(p, "arrival_missing", True),
                    "weather_missing": getattr(p, "weather_missing", True),
                    "feature_row_date": getattr(p, "feature_row_date", None)
                }
    except Exception as exc:
        logger.exception("Prediction generation error during reconciliation: %s", exc)
        prediction_service_status = "error"
        prediction_error_code = type(exc).__name__
        prediction_error_message = str(exc)

    # Resolve latest recorded price prior to or on selected date from DB or master-data
    latest_obs_record = db.query(CleanedMarketPrice).filter(
        CleanedMarketPrice.market_id == market_obj.id,
        CleanedMarketPrice.commodity_id == commodity_obj.id,
        CleanedMarketPrice.observation_date <= req.selected_date
    ).order_by(CleanedMarketPrice.observation_date.desc()).first()

    latest_price = float(latest_obs_record.modal_price) if (latest_obs_record and latest_obs_record.modal_price) else None
    latest_date_str = str(latest_obs_record.observation_date) if latest_obs_record else None

    if latest_price is None or latest_price <= 0:
        from app.services.master_data_service import find_latest_master_record
        m_rec = find_latest_master_record(req.commodity, req.market, max_date=req.selected_date)
        if m_rec:
            try:
                latest_price = float(m_rec.get("modal_price", 0))
            except Exception:
                latest_price = None
            latest_date_str = str(m_rec.get("date", req.selected_date))

    records: List[ForecastRecord] = []
    for d in forecast_dates:
        record = resolve_price_for_date(
            commodity=req.commodity,
            market=req.market,
            target_date=d,
            forecast_origin_date=req.selected_date,
            market_obj=market_obj,
            commodity_obj=commodity_obj,
            db=db,
            official_api_map=official_api_map,
            predictions_map=predictions_map,
            api_searched=True,
            now=now,
            feature_snapshot_id=feature_snapshot_id,
            model_version=model_ver,
            district=req.district,
            state=req.state,
            latest_recorded_price=latest_price,
            latest_recorded_date=latest_date_str
        )
        records.append(record)

    api_count = sum(1 for r in records if r.price_source == "official_api")
    csv_count = sum(1 for r in records if r.price_source == "official_csv")
    pred_model_count = sum(1 for r in records if r.price_source == "predicted_model")
    fallback_count = sum(1 for r in records if r.price_source == "fallback_last_observed")
    unavail_count = sum(1 for r in records if r.price_source == "unavailable")

    official_values_used = api_count + csv_count
    predicted_values_used = pred_model_count + fallback_count

    # Trend calculation with metadata
    start_rec = records[0] if records else None
    end_rec = records[-1] if records else None

    if start_rec and end_rec and start_rec.modal_price is not None and end_rec.modal_price is not None:
        start_p = start_rec.modal_price
        end_p = end_rec.modal_price
        diff = end_p - start_p
        pct_change = round((diff / (start_p + 1e-5)) * 100, 2)
        if pct_change > 1.5:
            trend_dir = "upward"
        elif pct_change < -1.5:
            trend_dir = "downward"
        else:
            trend_dir = "stable"

        if official_values_used > 0 and predicted_values_used > 0:
            trend_source = "observed_and_predicted"
        elif official_values_used > 0:
            trend_source = "purely_observed"
        else:
            trend_source = "purely_predicted"

        trend_start_date = str(start_rec.target_date or start_rec.date)
        trend_end_date = str(end_rec.target_date or end_rec.date)
        trend_start_price = start_p
        trend_end_price = end_p
    else:
        trend_dir = None
        pct_change = None
        trend_source = "unavailable"
        trend_start_date = None
        trend_end_date = None
        trend_start_price = None
        trend_end_price = None

    # Resolve latest observed price for base date directly from records[0] or exact market history
    if records and records[0].modal_price is not None:
        latest_price = records[0].modal_price
        latest_date_str = str(records[0].target_date or records[0].date or req.selected_date)
    else:
        latest_obs_record = db.query(CleanedMarketPrice).filter(
            CleanedMarketPrice.market_id == market_obj.id,
            CleanedMarketPrice.commodity_id == commodity_obj.id,
            CleanedMarketPrice.observation_date <= req.selected_date
        ).order_by(CleanedMarketPrice.observation_date.desc()).first()

        latest_price = float(latest_obs_record.modal_price) if (latest_obs_record and latest_obs_record.modal_price) else None
        latest_date_str = str(latest_obs_record.observation_date) if latest_obs_record else str(req.selected_date)

    latest_api_date = sync_summary.get("latest_api_date")
    latest_db_date = sync_summary.get("latest_db_date") or get_latest_official_date(db, req.commodity, req.market)
    
    # Calculate data age & stale warning
    data_age_days = (today_ist - latest_db_date).days if latest_db_date else 0
    warnings = []
    stale_warning = None
    if data_age_days > 2:
        stale_warning = f"Official data is from {latest_db_date} ({data_age_days} days old). Latest records were not available in data.gov.in."
        warnings.append(stale_warning)
    if sync_summary.get("api_status") == "failed":
        warnings.append(f"Live API synchronization failed ({sync_summary.get('error')}). Using latest verified database records.")

    response = VerifiedForecastResponse(
        request_id=req_id,
        commodity=req.commodity,
        market=req.market,
        district=req.district,
        state=req.state,
        selected_date=req.selected_date,
        forecast_origin_date=req.selected_date,
        date_range=DateRangeSummary(start=start_date, end=end_date),
        fetched_at=now,
        api_checked=True,
        api_status=api_status,
        sync_performed=api_checked,
        refresh_performed=req.force_refresh,
        latest_observed_price=latest_price,
        latest_observed_date=latest_date_str,
        trend_direction=trend_dir,
        percentage_change_3d=pct_change,
        trend_source=trend_source,
        trend_start_date=trend_start_date,
        trend_end_date=trend_end_date,
        trend_start_price=trend_start_price,
        trend_end_price=trend_end_price,
        official_values_used=official_values_used,
        predicted_values_used=predicted_values_used,
        records=records,
        summary={
            "official_api_count": api_count,
            "official_csv_count": csv_count,
            "predicted_model_count": pred_model_count,
            "fallback_last_observed_count": fallback_count,
            "predicted_count": pred_model_count + fallback_count,
            "unavailable_count": unavail_count,
            "official_values": official_values_used,
            "predicted_values": predicted_values_used,
            "unavailable_values": unavail_count
        },
        warnings=warnings,
        server_date=today_ist,
        future_dates_disabled=True,
        selected_date_valid=True,
        api_checked_time=now.strftime("%d %b %Y, %I:%M %p IST"),
        closest_market_status="active",
        model_version=model_ver,
        feature_snapshot_id=feature_snapshot_id,
        feature_schema_match=feature_schema_match,
        missing_features=missing_feats,
        unexpected_features=unexpected_feats,
        expected_feature_count=exp_feat_cnt,
        runtime_feature_count=run_feat_cnt,
        feature_explanations=feature_explanations,
        api_refresh_performed=True,
        api_latest_available_date=latest_api_date,
        database_latest_date=latest_db_date,
        feature_latest_date=parse_date_safely(feature_latest_date) if feature_latest_date else None,
        latest_official_api_date=latest_api_date,
        latest_stored_official_date=latest_db_date,
        latest_price_used_for_features=latest_price_used,
        latest_arrival_used_for_features=latest_arrival_used,
        data_refresh_status=api_status,
        data_age_days=data_age_days,
        stale_data_warning=stale_warning,
        records_fetched_count=sync_summary.get("records_accepted", 0),
        records_used_in_features=len(fresh_df) if not fresh_df.empty else 0,
        prediction_service_status=prediction_service_status,
        prediction_error_code=prediction_error_code,
        prediction_error_message=prediction_error_message
    )

    # Save live fetched JSON snapshot for audit, transparency, and frontend verification
    try:
        live_snapshot_payload = {
            "request_id": req_id,
            "fetched_at": now.isoformat(),
            "state": req.state,
            "district": req.district,
            "market": req.market,
            "commodity": req.commodity,
            "selected_date": req.selected_date.isoformat(),
            "latest_official_api_date": str(latest_api_date) if latest_api_date else None,
            "records": [r.model_dump() if hasattr(r, "model_dump") else r.dict() for r in records],
            "summary": response.summary,
            "server_date": str(today_ist)
        }
        save_live_fetched_json(live_snapshot_payload)
    except Exception as exc:
        logger.debug("Could not save live snapshot: %s", exc)

    return response

