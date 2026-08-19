import argparse
import os
import sys
import json
from datetime import datetime, date
import pandas as pd
import numpy as np

# Add backend directory to path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if not os.path.exists(BACKEND_DIR):
    BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.database import SessionLocal
from app.models import Market, Commodity, CleanedMarketPrice, ModelRun
from app.ml.model_registry import load_model_artifacts, get_model_path
from app.ml.dataset_builder import build_dataset_from_db
from app.ml.feature_engineering import FEATURE_COLUMNS, CATEGORICAL_FEATURES, NUMERIC_FEATURES
from app.ml.predict import generate_3day_prediction
from app.services.forecast_reconciliation_service import reconcile_verified_forecast
from app.schemas.forecast import VerifiedForecastRequest

def diagnose_pipeline(commodity: str, market: str, forecast_origin: str):
    print("=" * 70)
    print("          COMPREHENSIVE MODEL & PIPELINE DIAGNOSTIC          ")
    print("=" * 70)

    db = SessionLocal()
    diagnostic_passed = True
    failure_reasons = []

    try:
        origin_dt = datetime.strptime(forecast_origin, "%Y-%m-%d").date()

        # 1. Check Active Model Run
        active_run = db.query(ModelRun).filter(ModelRun.is_active == True).order_by(ModelRun.created_at.desc()).first()
        model_version = active_run.model_version if active_run else "v20260818_153724"
        print(f"Selected Commodity: {commodity}")
        print(f"Selected Market: {market}")
        print(f"Selected Forecast Origin Date: {forecast_origin}")
        print(f"Active Model Version: {model_version}")

        # 2. Check Model Artifact Files
        h1_path = get_model_path(model_version, 1)
        model_file_exists = os.path.exists(h1_path)
        print(f"Model Artifact Path (H1): {h1_path}")
        print(f"Model File Exists: {model_file_exists}")
        if not model_file_exists:
            diagnostic_passed = False
            failure_reasons.append("Model artifact file does not exist on disk.")

        models, metadata = load_model_artifacts(model_version)
        model_loaded = (models is not None and 1 in models and 2 in models and 3 in models)
        print(f"Model Loaded Successfully: {model_loaded} (Horizons: {list(models.keys()) if models else []})")
        if not model_loaded:
            diagnostic_passed = False
            failure_reasons.append("CatBoost models could not be loaded into memory.")

        # 3. Check Dataset & Feature Extraction
        print("\n--- FEATURE EXTRACTION & AUDIT ---")
        df_all = build_dataset_from_db(db)
        if df_all.empty:
            diagnostic_passed = False
            failure_reasons.append("Cleaned price database returned empty dataset.")
            print("ERROR: Cleaned price database returned empty dataset.")
            return False

        pred_res = generate_3day_prediction(
            db=db,
            commodity_name=commodity,
            market_name=market,
            prediction_date_str=forecast_origin,
            model_version=model_version,
            df_all=df_all
        )

        latest_observed_date = pred_res.get("latest_observed_date")
        latest_observed_price = pred_res.get("latest_observed_price")
        feature_row_date = pred_res.get("feature_row_date")
        days_gap = pred_res.get("days_between_feature_row_and_origin")

        print(f"Latest Observed Date Used: {latest_observed_date}")
        print(f"Latest Observed Price Used: Rs. {latest_observed_price}")
        print(f"Feature Row Date Used: {feature_row_date} (Lag relative to origin: {days_gap} days)")

        if feature_row_date and pd.to_datetime(feature_row_date).date() > origin_dt:
            diagnostic_passed = False
            failure_reasons.append(f"Feature row date {feature_row_date} is after the forecast origin {origin_dt} (Future Data Leakage!).")

        feature_count = pred_res.get("feature_count", 0)
        expected_features = metadata.get("feature_columns", FEATURE_COLUMNS)
        missing_features = [f for f in expected_features if f not in FEATURE_COLUMNS]

        print(f"Feature Count: {feature_count}")
        print(f"Missing Feature Count: {len(missing_features)}")
        print(f"Arrival Features Present: {pred_res.get('arrival_features_used', False)}")
        print(f"Weather Features Present: {pred_res.get('weather_features_used', False)}")
        print(f"Seasonal Features Present: {pred_res.get('seasonal_features_used', False)}")

        # 4. Check Model Prediction Execution
        print("\n--- MODEL PREDICTION EXECUTION ---")
        traces = pred_res.get("execution_traces", [])
        raw_outputs = {}
        for t in traces:
            h = t.get("horizon")
            raw_outputs[f"h{h}"] = t.get("raw_model_output")
            print(f"Horizon {h}: raw_output = Rs. {t.get('raw_model_output')} | executed = {t.get('prediction_executed')} | method = {t.get('prediction_method')} | fallback_reason = {t.get('fallback_reason')}")

            if not t.get("prediction_executed") and t.get("prediction_method") != "fallback":
                diagnostic_passed = False
                failure_reasons.append(f"Horizon {h} model was not executed.")

        # 5. Check API Forecast Reconciliation
        print("\n--- API FORECAST RECONCILIATION ---")
        req = VerifiedForecastRequest(
            commodity=commodity,
            market=market,
            selected_date=origin_dt,
            force_refresh=True
        )
        api_resp = reconcile_verified_forecast(db, req)
        api_outputs = {}
        for r in api_resp.records:
            if r.horizon and r.horizon > 0:
                api_outputs[f"h{r.horizon}"] = r.modal_price
        print(f"Final API Response Output: {api_outputs}")

        # 6. Sanity Checks: Equality, Fixed Offsets, Fixed Ratios
        print("\n--- GENUINENESS CHECKS ---")
        all_equal_to_last = False
        if latest_observed_price is not None:
            all_equal_to_last = all(
                raw_outputs.get(f"h{h}") is not None and abs(raw_outputs[f"h{h}"] - latest_observed_price) < 0.01
                for h in [1, 2, 3]
            )
        print(f"Output Equals Last Observed Price on All Horizons: {all_equal_to_last}")
        if all_equal_to_last:
            print("WARNING: Model output on all horizons is exactly equal to the last observed price (possible last value copy).")

        offsets = [raw_outputs[f"h{h}"] - latest_observed_price for h in [1, 2, 3] if raw_outputs.get(f"h{h}") is not None and latest_observed_price is not None]
        fixed_offset = len(set(offsets)) == 1 and len(offsets) == 3
        print(f"Output Uses Fixed Offset Adjustment: {fixed_offset}")

        # 7. Summary & Report Generation
        report = {
            "commodity": commodity,
            "market": market,
            "forecast_origin_date": forecast_origin,
            "latest_observed_date": latest_observed_date,
            "latest_observed_price": latest_observed_price,
            "feature_row_date": feature_row_date,
            "model_artifact_path": h1_path,
            "model_file_exists": model_file_exists,
            "model_loaded_successfully": model_loaded,
            "model_predict_executed": all(t.get("prediction_executed") for t in traces),
            "raw_model_output": raw_outputs,
            "final_api_output": api_outputs,
            "output_equals_last_observed_price": all_equal_to_last,
            "output_equals_fixed_offset": fixed_offset,
            "output_came_from_fallback": any(t.get("prediction_method") == "fallback" for t in traces),
            "feature_count": feature_count,
            "missing_feature_count": len(missing_features),
            "arrival_features_present": pred_res.get("arrival_features_used", False),
            "weather_features_present": pred_res.get("weather_features_used", False),
            "seasonal_features_present": pred_res.get("seasonal_features_used", False),
            "model_version": model_version,
            "diagnostic_passed": diagnostic_passed,
            "failure_reasons": failure_reasons
        }

        os.makedirs(os.path.join(os.path.dirname(__file__), "..", "reports"), exist_ok=True)
        report_path = os.path.join(os.path.dirname(__file__), "..", "reports", "prediction_pipeline_diagnostic.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print("-" * 70)
        if diagnostic_passed:
            print(">>> PIPELINE DIAGNOSTIC RESULT: PASSED <<<")
            print(f"Report written to: {report_path}")
            return True
        else:
            print(">>> PIPELINE DIAGNOSTIC RESULT: FAILED <<<")
            for r in failure_reasons:
                print(f"  - {r}")
            print(f"Report written to: {report_path}")
            return False

    except Exception as exc:
        print(f"Diagnostic encountered unexpected exception: {exc}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Diagnose price prediction pipeline")
    parser.add_argument("--commodity", type=str, default="Tomato")
    parser.add_argument("--market", type=str, default="Pattikonda APMC")
    parser.add_argument("--forecast-origin", type=str, default="2026-08-18")
    args = parser.parse_args()

    success = diagnose_pipeline(
        commodity=args.commodity,
        market=args.market,
        forecast_origin=args.forecast_origin
    )
    if not success:
        sys.exit(1)
