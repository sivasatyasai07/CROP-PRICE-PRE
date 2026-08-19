import numpy as np
from typing import Dict, Any, Tuple

def compute_conformal_intervals(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    target_coverage: float = 0.80,
    candidate_quantiles: list = [0.80, 0.75, 0.70, 0.65, 0.60]
) -> Tuple[float, float]:
    """
    Computes inductive conformal prediction margin from calibration residuals:
    margin = quantile(|y_true - y_pred|, 1 - alpha)
    Returns:
      (margin, selected_coverage_level)
    """
    if len(y_true) == 0 or len(y_pred) == 0:
        return 150.0, target_coverage

    residuals = np.abs(y_true - y_pred)
    n = len(residuals)
    
    # Conformal finite-sample correction: ceil((n+1)*(1-alpha))/n
    q_level = min(1.0, np.ceil((n + 1) * target_coverage) / n)
    margin = float(np.quantile(residuals, q_level))

    return max(margin, 10.0), target_coverage

def apply_prediction_interval(
    point_pred: float,
    margin: float,
    min_possible_price: float = 0.0
) -> Dict[str, float]:
    """
    Applies margin to point prediction ensuring nonnegative lower bound.
    """
    low = max(min_possible_price, point_pred - margin)
    high = point_pred + margin
    return {
        "predicted_modal_price": round(float(point_pred), 2),
        "lower_bound": round(float(low), 2),
        "upper_bound": round(float(high), 2),
        "margin": round(float(margin), 2)
    }
