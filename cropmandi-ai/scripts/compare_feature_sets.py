import os
import sys
import json
import numpy as np
import pandas as pd

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import SessionLocal
from app.ml.dataset_builder import build_dataset_from_db
from app.ml.feature_engineering import create_features, CATEGORICAL_FEATURES
from app.ml.time_series_split import chronological_split
from catboost import CatBoostRegressor, Pool

def evaluate_metrics(y_true, y_pred):
    mask = ~np.isnan(y_true) & ~np.isnan(y_pred)
    yt, yp = y_true[mask], y_pred[mask]
    if len(yt) == 0:
        return {"mae": 0, "rmse": 0, "wape": 0, "smape": 0, "dir_acc": 0}
    mae = float(np.mean(np.abs(yt - yp)))
    rmse = float(np.sqrt(np.mean((yt - yp) ** 2)))
    wape = float(np.sum(np.abs(yt - yp)) / (np.sum(yt) + 1e-5) * 100)
    smape = float(np.mean(2 * np.abs(yt - yp) / (np.abs(yt) + np.abs(yp) + 1e-5)) * 100)
    return {
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "wape": round(wape, 2),
        "smape": round(smape, 2)
    }

def main():
    print("Running Feature Set Ablation Comparison (Models A, B, C, D, E)...")
    db = SessionLocal()
    df_raw = build_dataset_from_db(db)
    db.close()

    if df_raw.empty:
        print("Error: No data available in DB.")
        return

    df_feats = create_features(df_raw, is_training=True)
    train_df, test_df = chronological_split(df_feats, train_end_date="2025-12-31")

    # Define Feature Sets
    feature_subsets = {
        "Model A (Price History Only)": [
            'market', 'commodity', 'district', 'lag_1', 'lag_2', 'lag_3', 'lag_7', 'lag_14',
            'rolling_mean_3', 'rolling_mean_7', 'rolling_mean_14', 'rolling_std_7',
            'price_change_1', 'price_change_3', 'price_vs_7_day_average'
        ],
        "Model B (Price + Arrival Quantity)": [
            'market', 'commodity', 'district', 'lag_1', 'lag_2', 'lag_3', 'lag_7', 'lag_14',
            'rolling_mean_3', 'rolling_mean_7', 'rolling_mean_14', 'rolling_std_7',
            'price_change_1', 'price_change_3', 'price_vs_7_day_average',
            'arrival_quantity_lag_1', 'arrival_quantity_lag_2', 'arrival_rolling_mean_7',
            'arrival_pressure', 'arrival_missing'
        ],
        "Model C (Price + Arrival + Calendar/Season)": [
            'market', 'commodity', 'district', 'lag_1', 'lag_2', 'lag_3', 'lag_7', 'lag_14',
            'rolling_mean_3', 'rolling_mean_7', 'rolling_mean_14', 'rolling_std_7',
            'price_change_1', 'price_change_3', 'price_vs_7_day_average',
            'arrival_quantity_lag_1', 'arrival_quantity_lag_2', 'arrival_rolling_mean_7',
            'arrival_pressure', 'arrival_missing',
            'month', 'day_of_week', 'day_of_year', 'is_weekend', 'sin_month', 'cos_month',
            'sin_day_of_year', 'cos_day_of_year', 'monsoon_flag', 'modal_price_lag_365'
        ],
        "Model D (Price + Arrival + Season + Weather)": [
            'market', 'commodity', 'district', 'lag_1', 'lag_2', 'lag_3', 'lag_7', 'lag_14',
            'rolling_mean_3', 'rolling_mean_7', 'rolling_mean_14', 'rolling_std_7',
            'price_change_1', 'price_change_3', 'price_vs_7_day_average',
            'arrival_quantity_lag_1', 'arrival_quantity_lag_2', 'arrival_rolling_mean_7',
            'arrival_pressure', 'arrival_missing',
            'month', 'day_of_week', 'day_of_year', 'is_weekend', 'sin_month', 'cos_month',
            'sin_day_of_year', 'cos_day_of_year', 'monsoon_flag', 'modal_price_lag_365',
            'temp_mean_clean', 'precip_clean', 'rainfall_7d', 'rainfall_14d', 'heavy_rain_flag', 'heat_stress_flag'
        ],
        "Model E (Full Pipeline: + Cross-Market Signals)": [
            'market', 'commodity', 'district', 'lag_1', 'lag_2', 'lag_3', 'lag_7', 'lag_14',
            'rolling_mean_3', 'rolling_mean_7', 'rolling_mean_14', 'rolling_std_7',
            'price_change_1', 'price_change_3', 'price_vs_7_day_average',
            'arrival_quantity_lag_1', 'arrival_quantity_lag_2', 'arrival_rolling_mean_7',
            'arrival_pressure', 'arrival_missing',
            'month', 'day_of_week', 'day_of_year', 'is_weekend', 'sin_month', 'cos_month',
            'sin_day_of_year', 'cos_day_of_year', 'monsoon_flag', 'modal_price_lag_365',
            'temp_mean_clean', 'precip_clean', 'rainfall_7d', 'rainfall_14d', 'heavy_rain_flag', 'heat_stress_flag',
            'same_day_regional_mean', 'same_day_regional_median', 'market_price_minus_regional_mean', 'regional_arrival_total'
        ]
    }

    report = {}
    print(f"\n{'Feature Set':<45} | {'Horizon':<8} | {'MAE':<8} | {'RMSE':<8} | {'WAPE (%)':<10} | {'sMAPE (%)':<10}")
    print("-" * 98)

    for set_name, feats in feature_subsets.items():
        report[set_name] = {}
        for h in [1, 2, 3]:
            target_col = f"target_h{h}"
            tr = train_df.dropna(subset=[target_col]).copy()
            te = test_df.dropna(subset=[target_col]).copy()

            if len(tr) < 30 or len(te) < 10:
                continue

            available_feats = [f for f in feats if f in tr.columns]
            cats = [f for f in available_feats if f in CATEGORICAL_FEATURES]

            X_tr = tr[available_feats].copy()
            y_tr = tr[target_col]
            X_te = te[available_feats].copy()
            y_te = te[target_col]

            for col in available_feats:
                if col not in cats:
                    X_tr[col] = X_tr[col].fillna(0.0)
                    X_te[col] = X_te[col].fillna(0.0)
                else:
                    X_tr[col] = X_tr[col].fillna("Unknown").astype(str)
                    X_te[col] = X_te[col].fillna("Unknown").astype(str)

            model = CatBoostRegressor(iterations=300, learning_rate=0.05, depth=5, random_seed=42, verbose=False)
            model.fit(Pool(X_tr, y_tr, cat_features=cats))

            preds = model.predict(Pool(X_te, cat_features=cats))
            m = evaluate_metrics(y_te.values, preds)
            report[set_name][f"horizon_{h}"] = m

            print(f"{set_name:<45} | H{h:<7} | {m['mae']:<8} | {m['rmse']:<8} | {m['wape']:<10} | {m['smape']:<10}")

    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "reports"), exist_ok=True)
    report_path = os.path.join(os.path.dirname(__file__), "..", "reports", "feature_ablation_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\nFeature ablation report saved to: {report_path}")

if __name__ == "__main__":
    main()
