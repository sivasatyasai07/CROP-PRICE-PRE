import numpy as np
import pandas as pd
from typing import Dict, Any, List

def calculate_baselines(test_df: pd.DataFrame, horizons: List[int] = [1, 2, 3]) -> Dict[str, Dict[str, float]]:
    """
    Computes baseline models on test set:
    1. Last observed price (naive)
    2. Last 3-day average
    3. 7-day seasonal naive
    """
    results = {}
    test_df = test_df.copy()

    for h in horizons:
        target_col = f"target_h{h}"
        if target_col not in test_df.columns:
            continue

        valid = test_df.dropna(subset=[target_col, 'lag_1']).copy()
        y_true = valid[target_col].values
        
        # 1. Naive last price
        y_naive = valid['lag_1'].values
        mae_naive = float(np.mean(np.abs(y_true - y_naive)))
        rmse_naive = float(np.sqrt(np.mean((y_true - y_naive) ** 2)))
        wape_naive = float(np.sum(np.abs(y_true - y_naive)) / (np.sum(y_true) + 1e-5) * 100)

        # 2. 3-day mean
        y_mean3 = valid.get('rolling_mean_3', valid['lag_1']).values
        mae_mean3 = float(np.mean(np.abs(y_true - y_mean3)))

        # 3. 7-day seasonal
        y_lag7 = valid.get('lag_7', valid['lag_1']).values
        mae_lag7 = float(np.mean(np.abs(y_true - y_lag7)))

        results[f"horizon_{h}"] = {
            "naive_last_price_mae": round(mae_naive, 2),
            "naive_last_price_rmse": round(rmse_naive, 2),
            "naive_last_price_wape": round(wape_naive, 2),
            "mean_3day_mae": round(mae_mean3, 2),
            "seasonal_7day_mae": round(mae_lag7, 2),
        }

    return results
