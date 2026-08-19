import pandas as pd
import numpy as np
from catboost import CatBoostRegressor, Pool
from app.ml.dataset_builder import FEATURE_COLUMNS, CATEGORICAL_FEATURES
from app.ml.model_registry import save_model_artifacts
from app.ml.evaluate import calculate_metrics, calculate_interval_metrics
from typing import Dict, Any, Tuple

NUMERIC_FEATURES = [c for c in FEATURE_COLUMNS if c not in CATEGORICAL_FEATURES]

def _prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """Fill NaN values: 0 for numeric features, leave categoricals intact for CatBoost."""
    out = df[FEATURE_COLUMNS].copy()
    out[NUMERIC_FEATURES] = out[NUMERIC_FEATURES].fillna(0)
    return out

def train_catboost_models(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    model_version: str = "1.0.0",
    iterations: int = 500,
    learning_rate: float = 0.05,
    depth: int = 6,
    target_coverage: float = 0.80
) -> Dict[str, Any]:
    models = {}
    metrics_summary = {}
    residual_std = {}
    conformal_q80 = {}
    conformal_quantile_level = {}

    for h in [1, 2, 3]:
        target_col = f"target_h{h}"
        
        train_sub = train_df.dropna(subset=[target_col]).copy()
        test_sub = test_df.dropna(subset=[target_col]).copy()
        
        if len(train_sub) < 20:
            continue

        # Sort chronologically for split
        if 'observation_date' in train_sub.columns:
            train_sub = train_sub.sort_values('observation_date')

        # Split training into fit (70%), calibration (15%), validation (15%)
        n = len(train_sub)
        calib_start = int(n * 0.70)
        val_start = int(n * 0.85)
        fit_sub = train_sub.iloc[:calib_start]
        calib_sub = train_sub.iloc[calib_start:val_start]
        val_sub = train_sub.iloc[val_start:]

        if len(fit_sub) < 10 or len(calib_sub) < 5:
            # Fall back to 80/20 if not enough data for 3-way split
            calib_start = int(n * 0.80)
            fit_sub = train_sub.iloc[:calib_start]
            calib_sub = train_sub.iloc[calib_start:]
            val_sub = calib_sub  # validation = calibration in this case

        X_fit = _prepare_features(fit_sub)
        y_fit = fit_sub[target_col]

        X_calib = _prepare_features(calib_sub)
        y_calib = calib_sub[target_col]

        X_val = _prepare_features(val_sub)
        y_val = val_sub[target_col]

        X_test = _prepare_features(test_sub)
        y_test = test_sub[target_col]

        fit_pool = Pool(X_fit, y_fit, cat_features=CATEGORICAL_FEATURES)
        calib_pool = Pool(X_calib, y_calib, cat_features=CATEGORICAL_FEATURES)

        model = CatBoostRegressor(
            iterations=iterations,
            learning_rate=learning_rate,
            depth=depth,
            loss_function='RMSE',
            eval_metric='RMSE',
            random_seed=42,
            verbose=False
        )

        # Early stopping on calibration set (never test set)
        model.fit(fit_pool, eval_set=calib_pool, early_stopping_rounds=50)
        models[h] = model

        # Inductive conformal: compute residuals on calibration set
        calib_preds = model.predict(calib_pool)
        calib_residuals = np.abs(y_calib.values - calib_preds)
        residual_std[h] = float(np.std(calib_residuals)) if len(calib_residuals) > 0 else 150.0

        # Adaptive quantile: start at target_coverage, validate on val set,
        # step down if over-covering to achieve tighter, more useful intervals
        val_preds = model.predict(Pool(X_val, cat_features=CATEGORICAL_FEATURES))
        best_q_level = target_coverage
        best_margin = float(np.quantile(calib_residuals, best_q_level))

        for candidate_level in [target_coverage, 0.70, 0.60, 0.50]:
            candidate_margin = float(np.quantile(calib_residuals, candidate_level))
            val_coverage = float(np.mean(
                (y_val.values >= val_preds - candidate_margin) &
                (y_val.values <= val_preds + candidate_margin)
            ))
            # Accept the tightest interval that still achieves >= target coverage on validation
            if val_coverage >= target_coverage:
                best_q_level = candidate_level
                best_margin = candidate_margin
            else:
                break  # Stop tightening once we drop below target

        conformal_q80[h] = best_margin
        conformal_quantile_level[h] = best_q_level

        # Out-of-sample evaluation on test set
        if len(X_test) > 0:
            test_pool = Pool(X_test, cat_features=CATEGORICAL_FEATURES)
            test_preds = model.predict(test_pool)
            metrics = calculate_metrics(y_test.values, test_preds)
            
            # Evaluate empirical conformal coverage on test set
            lower_b = test_preds - best_margin
            upper_b = test_preds + best_margin
            
            interval_m = calculate_interval_metrics(y_test.values, lower_b, upper_b)
            metrics["quantile_level_used"] = best_q_level
            metrics.update(interval_m)
            metrics_summary[f"horizon_{h}"] = metrics

    metadata = {
        "model_version": model_version,
        "feature_columns": FEATURE_COLUMNS,
        "categorical_features": CATEGORICAL_FEATURES,
        "residual_std": residual_std,
        "conformal_q80": conformal_q80,
        "conformal_quantile_level": conformal_quantile_level,
        "metrics": metrics_summary
    }

    save_model_artifacts(model_version, models, metadata)
    return metadata
