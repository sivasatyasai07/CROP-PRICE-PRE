import pandas as pd
import numpy as np
from typing import List

def build_direct_horizon_targets(df: pd.DataFrame, horizons: List[int] = [1, 2, 3]) -> pd.DataFrame:
    """
    Constructs direct multi-horizon forecasting targets:
    target_h1 = modal_price at t+1
    target_h2 = modal_price at t+2
    target_h3 = modal_price at t+3
    Computed strictly per (market, commodity) series sorted chronologically by observation_date.
    """
    df = df.copy()
    if 'observation_date' in df.columns:
        df['observation_date'] = pd.to_datetime(df['observation_date'])
        df = df.sort_values(by=['market', 'commodity', 'observation_date']).reset_index(drop=True)

    grouped = df.groupby(['market', 'commodity'])

    for h in horizons:
        df[f'target_h{h}'] = grouped['modal_price'].shift(-h)

    return df
