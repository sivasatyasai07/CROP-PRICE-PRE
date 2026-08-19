import argparse
import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import SessionLocal
from app.models import ModelRun
from app.ml.dataset_builder import build_dataset_from_db
from app.ml.time_series_split import chronological_split
from app.ml.train_models import train_direct_horizon_models
from app.ml.model_selection import calculate_baselines

def main():
    parser = argparse.ArgumentParser(description="Train CatBoost direct multi-horizon models and evaluate baselines")
    parser.add_argument("--train-start", type=str, default="2021-01-01")
    parser.add_argument("--train-end", type=str, default="2025-12-31")
    parser.add_argument("--test-start", type=str, default="2026-01-01")
    args = parser.parse_args()

    print(f"Starting CatBoost Direct Multi-Horizon Training (Train <= {args.train_end}, Test >= {args.test_start})...")
    db = SessionLocal()
    try:
        df_all = build_dataset_from_db(db)
        if df_all.empty:
            print("Error: Empty dataset.")
            sys.exit(1)

        train_df, test_df = chronological_split(df_all, train_end_date=args.train_end)
        print(f"Training records: {len(train_df)} | Test records: {len(test_df)}")

        # 1. Compute Baselines
        baselines = calculate_baselines(test_df)
        print("\n--- BASELINE BENCHMARKS (Test Set 2026) ---")
        for h, b_met in baselines.items():
            print(f"  {h.upper()}: Naive MAE = {b_met['naive_last_price_mae']} Rs. | 3-Day Mean MAE = {b_met['mean_3day_mae']} Rs. | Seasonal 7-Day MAE = {b_met['seasonal_7day_mae']} Rs.")

        # 2. Train Direct Models
        model_version = f"v{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        train_res = train_direct_horizon_models(train_df, test_df, model_version=model_version)

        # 3. Update ModelRun record in DB
        db.query(ModelRun).update({"is_active": False})
        model_run = ModelRun(
            model_name="CatBoostRegressor Direct Multi-Horizon",
            model_version=model_version,
            training_start_date=datetime.strptime(args.train_start, "%Y-%m-%d").date(),
            training_end_date=datetime.strptime(args.train_end, "%Y-%m-%d").date(),
            test_start_date=datetime.strptime(args.test_start, "%Y-%m-%d").date(),
            training_rows=len(train_df),
            metrics_json=json.dumps({"catboost": train_res.get("metrics"), "baselines": baselines}),
            artifact_path=f"ml/models/catboost_h1_v{model_version}.cbm",
            status="completed",
            is_active=True
        )
        db.add(model_run)
        db.commit()

        print("\n--- MODEL TRAINING COMPLETE ---")
        print(f"Active Model Version: {model_version}")
        print("Out-of-Sample Performance on 2026 Test Set:")
        for h_key, metrics in train_res.get("metrics", {}).items():
            print(f"  {h_key.upper()}: MAE={metrics['mae']} Rs. | RMSE={metrics['rmse']} | WAPE={metrics['wape']}% | R2={metrics['r2']}")
        print("-------------------------------\n")

        # Save model comparison report
        os.makedirs(os.path.join(os.path.dirname(__file__), "..", "reports"), exist_ok=True)
        report_path = os.path.join(os.path.dirname(__file__), "..", "reports", "model_comparison_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump({
                "model_version": model_version,
                "catboost_metrics": train_res.get("metrics"),
                "baseline_metrics": baselines,
                "top_features": train_res.get("feature_importances")
            }, f, indent=2)
        print(f"Model comparison report saved to: {report_path}")

    except Exception as e:
        print(f"Training failed: {str(e)}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
