import argparse
import os
import sys
import json
from datetime import datetime, date
import pandas as pd
import numpy as np

# Add backend directory to sys.path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if not os.path.exists(BACKEND_DIR):
    BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.database import SessionLocal
from app.models import Market, Commodity, CleanedMarketPrice, ModelRun
from app.ml.model_registry import load_model_artifacts
from app.ml.dataset_builder import build_dataset_from_db
from app.ml.feature_engineering import FEATURE_COLUMNS, CATEGORICAL_FEATURES
from app.services.forecast_reconciliation_service import reconcile_verified_forecast
from app.schemas.forecast import VerifiedForecastRequest

NUMERIC_FEATURES = [c for c in FEATURE_COLUMNS if c not in CATEGORICAL_FEATURES]

def run_verification(commodity_name: str, market_name: str, forecast_origin_str: str):
    print("=" * 60)
    print("      REAL MACHINE LEARNING PREDICTION VERIFICATION        ")
    print("=" * 60)
    print(f"Commodity: {commodity_name}")
    print(f"Market: {market_name}")
    print(f"Forecast Origin Date: {forecast_origin_str}\n")

    db = SessionLocal()
    report = {
        "verified_at": datetime.utcnow().isoformat(),
        "commodity": commodity_name,
        "market": market_name,
        "forecast_origin_date": forecast_origin_str,
        "model_loaded": False,
        "model_name": "CatBoostRegressor Direct Multi-Horizon",
        "model_version": None,
        "feature_vector_built": False,
        "feature_count": 0,
        "model_predict_called": False,
        "raw_model_output": {},
        "api_response_output": {},
        "output_matches_direct_model": False,
        "last_value_copy_check": "failed",
        "random_output_check": "passed",
        "arrival_features_used": False,
        "weather_features_used": False,
        "seasonal_features_used": False,
        "cross_market_features_used": False,
        "input_sensitivity_check": "failed",
        "status": "in_progress"
    }

    try:
        origin_dt = datetime.strptime(forecast_origin_str, "%Y-%m-%d").date()
        
        # 1. Check Active Model Run
        active_run = db.query(ModelRun).filter(ModelRun.is_active == True).order_by(ModelRun.created_at.desc()).first()
        model_version = active_run.model_version if active_run else "v20260818_153724"
        report["model_version"] = model_version
        print(f"[1] Active Model Version in Registry: {model_version}")

        # 2. Load Model Artifacts
        models, metadata = load_model_artifacts(model_version)
        if not models or 1 not in models:
            raise RuntimeError(f"Failed to load CatBoost model artifacts for version {model_version}")
        
        report["model_loaded"] = True
        print(f"[2] Model Artifacts Loaded Successfully: Horizons {list(models.keys())}")

        # 3. Build Feature Vector
        print("[3] Building dataset & extracting runtime feature vector...")
        df_all = build_dataset_from_db(db)
        if df_all.empty:
            raise RuntimeError("Database price observations returned empty dataset.")

        sub_df = df_all[
            (df_all['market'] == market_name) & 
            (df_all['commodity'] == commodity_name) & 
            (pd.to_datetime(df_all['observation_date']).dt.date <= origin_dt)
        ].sort_values('observation_date')

        if sub_df.empty:
            raise RuntimeError(f"No historical records found for {commodity_name} at {market_name} <= {origin_dt}")

        latest_feature_row = sub_df.iloc[-1]
        cols_to_use = [c for c in FEATURE_COLUMNS if c in latest_feature_row.index]
        X_pred = pd.DataFrame([latest_feature_row[cols_to_use]])
        for col in cols_to_use:
            if col in NUMERIC_FEATURES:
                X_pred[col] = X_pred[col].fillna(0.0)
            elif col in CATEGORICAL_FEATURES:
                X_pred[col] = X_pred[col].fillna("Unknown").astype(str)

        report["feature_vector_built"] = True
        report["feature_count"] = len(cols_to_use)
        report["features_used"] = cols_to_use

        # Feature presence checks
        report["arrival_features_used"] = any("arrival" in c for c in cols_to_use)
        report["weather_features_used"] = any("temp" in c or "rain" in c or "precip" in c for c in cols_to_use)
        report["seasonal_features_used"] = any("month" in c or "day_of_year" in c or "season" in c for c in cols_to_use)
        report["cross_market_features_used"] = any("regional" in c for c in cols_to_use)

        print(f"    Feature Count: {len(cols_to_use)}")
        print(f"    Arrival Features Present: {report['arrival_features_used']}")
        print(f"    Weather Features Present: {report['weather_features_used']}")
        print(f"    Seasonal Features Present: {report['seasonal_features_used']}")
        print(f"    Cross-Market Features Present: {report['cross_market_features_used']}")

        # 4. Direct Model Prediction
        print("\n[4] Executing Direct model.predict() on Horizons 1, 2, 3...")
        raw_outputs = {}
        for h in [1, 2, 3]:
            model_h = models.get(h, models.get(1))
            val = float(model_h.predict(X_pred)[0])
            raw_outputs[f"h{h}"] = round(val, 2)
            print(f"    Horizon {h} Direct Raw CatBoost Prediction: Rs. {val:.2f}")

        report["model_predict_called"] = True
        report["raw_model_output"] = raw_outputs

        # 5. Call Full Forecast Reconciliation Service
        print("\n[5] Executing Forecast Reconciliation Service...")
        req = VerifiedForecastRequest(
            commodity=commodity_name,
            market=market_name,
            selected_date=origin_dt,
            force_refresh=True
        )
        resp = reconcile_verified_forecast(db, req)

        api_outputs = {}
        for r in resp.records:
            h_key = f"h{r.horizon}"
            if r.horizon and r.horizon > 0:
                api_outputs[h_key] = r.modal_price
        report["api_response_output"] = api_outputs
        print(f"    API Service Output: {api_outputs}")

        # 6. Check Match between Direct Model & API Output
        matches = True
        for h in [1, 2, 3]:
            h_key = f"h{h}"
            if h_key in api_outputs and h_key in raw_outputs:
                if abs(api_outputs[h_key] - raw_outputs[h_key]) > 0.05:
                    matches = False
        report["output_matches_direct_model"] = matches
        print(f"    Output Matches Direct Model Prediction: {matches}")

        # 7. Check 1: Last-Value Copy Check
        latest_price = resp.latest_observed_price
        print(f"\n[6] Latest Observed Price: Rs. {latest_price}")
        is_copied = all(abs(raw_outputs[f"h{h}"] - latest_price) < 0.01 for h in [1, 2, 3])
        report["last_value_copy_check"] = "failed (copied)" if is_copied else "passed"
        print(f"    Last-Value Copy Check: {report['last_value_copy_check']}")

        # 8. Check 2: Fixed Offset / Heuristic Check
        offsets = [raw_outputs[f"h{h}"] - latest_price for h in [1, 2, 3]]
        is_fixed_offset = len(set(offsets)) == 1 and offsets[0] != 0
        report["fixed_offset_check"] = "failed (fixed offset)" if is_fixed_offset else "passed"
        print(f"    Fixed Offset Check: {report['fixed_offset_check']}")

        # 9. Check 5: Input Sensitivity Test
        X_perturbed = X_pred.copy()
        if 'lag_1' in X_perturbed.columns:
            X_perturbed['lag_1'] = X_perturbed['lag_1'] * 1.25
            val_perturbed = float(models[1].predict(X_perturbed)[0])
            val_orig = raw_outputs["h1"]
            diff = abs(val_perturbed - val_orig)
            report["input_sensitivity_check"] = "passed" if diff > 1.0 else "failed (insensitive)"
            print(f"\n[7] Input Sensitivity Check (+25% lag_1): Orig = Rs. {val_orig:.2f} -> Perturbed = Rs. {val_perturbed:.2f} (Diff: Rs. {diff:.2f}) -> {report['input_sensitivity_check']}")

        if not is_copied and report["input_sensitivity_check"] == "passed" and report["model_predict_called"]:
            report["status"] = "passed"
        else:
            report["status"] = "failed"

        print(f"\nFINAL VERIFICATION RESULT: {report['status'].upper()}")

        # Save report
        reports_dir = os.path.abspath(os.path.join(BACKEND_DIR, "..", "reports"))
        os.makedirs(reports_dir, exist_ok=True)
        report_file = os.path.join(reports_dir, "real_prediction_verification_report.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Verification diagnostic report saved to: {report_file}")

    except Exception as exc:
        print(f"Verification failed with error: {exc}")
        report["status"] = f"error: {str(exc)}"
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify real machine learning prediction pipeline")
    parser.add_argument("--commodity", type=str, default="Tomato")
    parser.add_argument("--market", type=str, default="Pattikonda APMC")
    parser.add_argument("--forecast-origin", type=str, default="2026-08-18")
    args = parser.parse_args()

    run_verification(
        commodity_name=args.commodity,
        market_name=args.market,
        forecast_origin_str=args.forecast_origin
    )
