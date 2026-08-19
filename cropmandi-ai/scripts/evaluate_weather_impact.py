import os
import sys
import json
import numpy as np
import pandas as pd

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
        return {"mae": 0, "rmse": 0, "wape": 0}
    mae = float(np.mean(np.abs(yt - yp)))
    rmse = float(np.sqrt(np.mean((yt - yp) ** 2)))
    wape = float(np.sum(np.abs(yt - yp)) / (np.sum(yt) + 1e-5) * 100)
    return {"mae": round(mae, 2), "rmse": round(rmse, 2), "wape": round(wape, 2)}

def main():
    print("Evaluating Weather Feature Impact Across Crops and Horizons...")
    db = SessionLocal()
    df_raw = build_dataset_from_db(db)
    db.close()

    if df_raw.empty:
        print("Error: No data available.")
        return

    df_feats = create_features(df_raw, is_training=True)
    train_df, test_df = chronological_split(df_feats, train_end_date="2025-12-31")

    base_cols = [
        'market', 'commodity', 'district', 'lag_1', 'lag_2', 'lag_3', 'lag_7',
        'rolling_mean_3', 'rolling_mean_7', 'rolling_mean_14',
        'arrival_quantity_lag_1', 'arrival_pressure', 'month', 'sin_month', 'cos_month'
    ]

    weather_cols = [
        'temp_mean_clean', 'precip_clean', 'rainfall_7d', 'rainfall_14d',
        'heavy_rain_flag', 'heat_stress_flag', 'crop_short_rainfall'
    ]

    crops = ["Tomato", "Paddy", "Onion", "Potato", "Dry Chillies", "Maize"]
    crop_eval = {}

    print(f"\n{'Crop':<15} | {'Horizon':<8} | {'No-Weather MAE':<15} | {'With-Weather MAE':<18} | {'Improvement':<12}")
    print("-" * 75)

    for crop in crops:
        crop_eval[crop] = {}
        for h in [1, 2, 3]:
            target_col = f"target_h{h}"
            tr = train_df[(train_df['commodity'] == crop) & train_df[target_col].notna()].copy()
            te = test_df[(test_df['commodity'] == crop) & test_df[target_col].notna()].copy()

            if len(tr) < 20 or len(te) < 5:
                continue

            cats = [c for c in base_cols if c in CATEGORICAL_FEATURES]

            # 1. Model without weather
            X_tr_no_w = tr[base_cols].copy()
            X_te_no_w = te[base_cols].copy()
            for col in base_cols:
                if col not in cats:
                    X_tr_no_w[col] = X_tr_no_w[col].fillna(0.0)
                    X_te_no_w[col] = X_te_no_w[col].fillna(0.0)
                else:
                    X_tr_no_w[col] = X_tr_no_w[col].fillna("Unknown").astype(str)
                    X_te_no_w[col] = X_te_no_w[col].fillna("Unknown").astype(str)

            m_no_w = CatBoostRegressor(iterations=250, learning_rate=0.05, depth=5, random_seed=42, verbose=False)
            m_no_w.fit(Pool(X_tr_no_w, tr[target_col], cat_features=cats))
            preds_no_w = m_no_w.predict(Pool(X_te_no_w, cat_features=cats))
            met_no_w = evaluate_metrics(te[target_col].values, preds_no_w)

            # 2. Model with weather
            w_cols = base_cols + weather_cols
            X_tr_w = tr[w_cols].copy()
            X_te_w = te[w_cols].copy()
            for col in w_cols:
                if col not in cats:
                    X_tr_w[col] = X_tr_w[col].fillna(0.0)
                    X_te_w[col] = X_te_w[col].fillna(0.0)
                else:
                    X_tr_w[col] = X_tr_w[col].fillna("Unknown").astype(str)
                    X_te_w[col] = X_te_w[col].fillna("Unknown").astype(str)

            m_w = CatBoostRegressor(iterations=250, learning_rate=0.05, depth=5, random_seed=42, verbose=False)
            m_w.fit(Pool(X_tr_w, tr[target_col], cat_features=cats))
            preds_w = m_w.predict(Pool(X_te_w, cat_features=cats))
            met_w = evaluate_metrics(te[target_col].values, preds_w)

            imp_diff = round(met_no_w["mae"] - met_w["mae"], 2)
            imp_status = f"+{imp_diff} ₹" if imp_diff > 0 else f"{imp_diff} ₹"

            crop_eval[crop][f"horizon_{h}"] = {
                "no_weather": met_no_w,
                "with_weather": met_w,
                "mae_difference": imp_diff,
                "weather_beneficial": imp_diff >= 0
            }

            print(f"{crop:<15} | H{h:<7} | {met_no_w['mae']:<15} | {met_w['mae']:<18} | {imp_status:<12}")

    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "reports"), exist_ok=True)
    report_path = os.path.join(os.path.dirname(__file__), "..", "reports", "weather_impact_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(crop_eval, f, indent=2)

    print(f"\nWeather impact report saved to: {report_path}")

if __name__ == "__main__":
    main()
