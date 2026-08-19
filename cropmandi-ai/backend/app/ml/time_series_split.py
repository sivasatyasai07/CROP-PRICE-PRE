import pandas as pd
from typing import List, Tuple, Dict, Any

def chronological_split(
    df: pd.DataFrame,
    train_end_date: str = "2025-12-31",
    date_col: str = "observation_date"
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Performs strict chronological train / test split.
    Train: dates <= train_end_date
    Test: dates > train_end_date
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    cutoff = pd.to_datetime(train_end_date)

    train_df = df[df[date_col] <= cutoff].reset_index(drop=True)
    test_df = df[df[date_col] > cutoff].reset_index(drop=True)

    return train_df, test_df

def generate_walk_forward_folds(
    df: pd.DataFrame,
    folds_config: List[Dict[str, str]],
    date_col: str = "observation_date"
) -> List[Tuple[str, pd.DataFrame, pd.DataFrame]]:
    """
    Generates expanding-window walk-forward folds without future leakage:
    Fold 1: train <= 2023, validate 2024
    Fold 2: train <= 2024, validate 2025
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    folds = []

    for fold in folds_config:
        name = fold["name"]
        train_end = pd.to_datetime(fold["train_end"])
        val_start = pd.to_datetime(fold["val_start"])
        val_end = pd.to_datetime(fold["val_end"])

        train_fold = df[df[date_col] <= train_end].reset_index(drop=True)
        val_fold = df[(df[date_col] >= val_start) & (df[date_col] <= val_end)].reset_index(drop=True)

        folds.append((name, train_fold, val_fold))

    return folds
