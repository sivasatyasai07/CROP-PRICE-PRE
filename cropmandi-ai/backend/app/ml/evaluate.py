import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple

def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    
    # Exclude NaNs
    mask = ~np.isnan(y_true) & ~np.isnan(y_pred)
    yt = y_true[mask]
    yp = y_pred[mask]
    
    if len(yt) == 0:
        return {"mae": 0, "rmse": 0, "mape": 0, "wape": 0, "smape": 0, "r2": 0, "count": 0}

    mae = float(np.mean(np.abs(yt - yp)))
    rmse = float(np.sqrt(np.mean((yt - yp) ** 2)))
    
    # Avoid zero division in MAPE
    non_zero_mask = (yt != 0)
    yt_nz = yt[non_zero_mask]
    yp_nz = yp[non_zero_mask]
    
    mape = float(np.mean(np.abs((yt_nz - yp_nz) / yt_nz)) * 100) if len(yt_nz) > 0 else 0.0
    wape = float(np.sum(np.abs(yt - yp)) / (np.sum(yt) + 1e-5) * 100)
    
    smape_denom = (np.abs(yt) + np.abs(yp)) / 2.0
    smape_mask = (smape_denom != 0)
    smape = float(np.mean(np.abs(yt[smape_mask] - yp[smape_mask]) / smape_denom[smape_mask]) * 100) if np.any(smape_mask) else 0.0

    # R2 calculation
    ss_res = np.sum((yt - yp) ** 2)
    ss_tot = np.sum((yt - np.mean(yt)) ** 2)
    r2 = float(1 - (ss_res / (ss_tot + 1e-5)))

    return {
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "mape": round(mape, 2),
        "wape": round(wape, 2),
        "smape": round(smape, 2),
        "r2": round(r2, 4),
        "count": int(len(yt)),
        "zero_excluded_mape_count": int(len(yt) - len(yt_nz))
    }

def calculate_interval_metrics(y_true: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> Dict[str, float]:
    y_true = np.array(y_true, dtype=float)
    lower = np.array(lower, dtype=float)
    upper = np.array(upper, dtype=float)
    
    mask = ~np.isnan(y_true) & ~np.isnan(lower) & ~np.isnan(upper)
    yt = y_true[mask]
    low = lower[mask]
    up = upper[mask]
    
    if len(yt) == 0:
        return {"coverage": 0.0, "avg_width": 0.0}

    covered = (yt >= low) & (yt <= up)
    coverage = float(np.mean(covered) * 100)
    avg_width = float(np.mean(up - low))

    return {
        "coverage": round(coverage, 2),
        "avg_width": round(avg_width, 2)
    }
