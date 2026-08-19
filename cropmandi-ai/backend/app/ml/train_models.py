import os
import sys
import numpy as np
import pandas as pd
# Add backend directory to PYTHONPATH for package imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from catboost import CatBoostRegressor, Pool
from typing import Dict, Any, Tuple

from app.ml.feature_engineering import FEATURE_COLUMNS, CATEGORICAL_FEATURES
from app.ml.prediction_intervals import compute_conformal_intervals
from app.ml.evaluate import calculate_metrics
from app.ml.model_registry import save_model_artifacts
from app.ml.feature_importance import extract_feature_importance

NUMERIC_FEATURES = [c for c in FEATURE_COLUMNS if c not in CATEGORICAL_FEATURES]

def prepare_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Fills NaNs in numeric features and retains categoricals for CatBoost."""
    cols_to_use = [c for c in FEATURE_COLUMNS if c in df.columns]
    out = df[cols_to_use].copy()
    for col in cols_to_use:
        if col in NUMERIC_FEATURES:
            out[col] = out[col].fillna(0.0)
        elif col in CATEGORICAL_FEATURES:
            out[col] = out[col].fillna("Unknown").astype(str)
    return out

def train_direct_horizon_models(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    model_version: str = "2.1.0",
    iterations: int = 600,
    learning_rate: float = 0.04,
    depth: int = 6
) -> Dict[str, Any]:
    """
    Trains separate direct CatBoost models for horizon 1, 2, and 3:
    target_h1, target_h2, target_h3.
    Extracts conformal residuals and evaluates out-of-sample metrics.
    """
    models = {}
    metrics_summary = {}
    residual_std = {}
    conformal_margins = {}
    feature_importances = {}

    for h in [1, 2, 3]:
        target_col = f"target_h{h}"
        if target_col not in train_df.columns:
            continue

        train_sub = train_df.dropna(subset=[target_col]).copy()
        test_sub = test_df.dropna(subset=[target_col]).copy()

        if len(train_sub) < 20:
            continue

        if 'observation_date' in train_sub.columns:
            train_sub = train_sub.sort_values('observation_date')

        # Split training into fit (75%), calibration (15%), validation (10%)
        n = len(train_sub)
        calib_start = int(n * 0.75)
        val_start = int(n * 0.90)

        fit_sub = train_sub.iloc[:calib_start]
        calib_sub = train_sub.iloc[calib_start:val_start]
        val_sub = train_sub.iloc[val_start:]

        X_fit = prepare_feature_matrix(fit_sub)
        y_fit = fit_sub[target_col]

        X_calib = prepare_feature_matrix(calib_sub)
        y_calib = calib_sub[target_col]

        X_val = prepare_feature_matrix(val_sub)
        y_val = val_sub[target_col]

        X_test = prepare_feature_matrix(test_sub)
        y_test = test_sub[target_col]

        fit_pool = Pool(X_fit, y_fit, cat_features=CATEGORICAL_FEATURES)
        calib_pool = Pool(X_calib, y_calib, cat_features=CATEGORICAL_FEATURES)
        test_pool = Pool(X_test, y_test, cat_features=CATEGORICAL_FEATURES)

        model = CatBoostRegressor(
            iterations=iterations,
            learning_rate=learning_rate,
            depth=depth,
            loss_function='RMSE',
            eval_metric='RMSE',
            random_seed=42,
            verbose=False
        )

        model.fit(fit_pool, eval_set=calib_pool, early_stopping_rounds=50)
        models[h] = model

        # Conformal intervals on calibration set
        calib_preds = model.predict(calib_pool)
        margin, _ = compute_conformal_intervals(y_calib.values, calib_preds, target_coverage=0.80)
        conformal_margins[h] = margin
        residual_std[h] = float(np.std(np.abs(y_calib.values - calib_preds))) if len(calib_preds) > 0 else 150.0

        # Out-of-sample evaluation on test set (2026 data)
        test_preds = model.predict(test_pool)
        h_metrics = calculate_metrics(y_test.values, test_preds)
        metrics_summary[f"horizon_{h}"] = h_metrics

        # Feature importance
        feature_importances[f"horizon_{h}"] = extract_feature_importance(model, list(X_fit.columns), top_n=10)

    # Save artifacts
    metadata = {
        "model_version": model_version,
        "feature_columns": [c for c in FEATURE_COLUMNS if c in train_df.columns],
        "categorical_features": CATEGORICAL_FEATURES,
        "metrics": metrics_summary,
        "residual_std": residual_std,
        "conformal_q80": conformal_margins,
    }
    save_model_artifacts(
        model_version,
        models,
        metadata,
    )

    return {
        "models": models,
        "metrics": metrics_summary,
        "conformal_margins": conformal_margins,
        "residual_std": residual_std,
        "feature_importances": feature_importances,
        "model_version": model_version
    }
