import pandas as pd
import numpy as np

def build_cross_market_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes cross-market regional features for each (commodity, observation_date) strictly from past/same-day observations:
    - same_day_regional_mean, same_day_regional_median, same_day_regional_min, same_day_regional_max, same_day_regional_std
    - market_price_minus_regional_mean, market_price_ratio_to_regional_mean
    - number_of_markets_reporting
    - regional_arrival_total, regional_arrival_mean
    """
    df = df.copy()

    # Calculate regional price metrics based on lag_1 to strictly prevent target leakage
    if 'lag_1' not in df.columns:
        df['lag_1'] = df.groupby(['market', 'commodity'])['modal_price'].shift(1)

    cross_price_grp = df.groupby(['commodity', 'observation_date'])['lag_1']
    df['same_day_regional_mean'] = cross_price_grp.transform('mean').fillna(df['lag_1']).fillna(0.0)
    df['same_day_regional_median'] = cross_price_grp.transform('median').fillna(df['lag_1']).fillna(0.0)
    df['same_day_regional_min'] = cross_price_grp.transform('min').fillna(df['lag_1']).fillna(0.0)
    df['same_day_regional_max'] = cross_price_grp.transform('max').fillna(df['lag_1']).fillna(0.0)
    df['same_day_regional_std'] = cross_price_grp.transform('std').fillna(0.0)

    df['market_price_minus_regional_mean'] = df['lag_1'] - df['same_day_regional_mean']
    df['market_price_ratio_to_regional_mean'] = df['lag_1'] / (df['same_day_regional_mean'] + 1e-5)
    df['number_of_markets_reporting'] = cross_price_grp.transform('count').fillna(1).astype(int)

    if 'arrival_quantity_lag_1' in df.columns:
        cross_arr_grp = df.groupby(['commodity', 'observation_date'])['arrival_quantity_lag_1']
        df['regional_arrival_total'] = cross_arr_grp.transform('sum').fillna(0.0)
        df['regional_arrival_mean'] = cross_arr_grp.transform('mean').fillna(0.0)
    else:
        df['regional_arrival_total'] = 0.0
        df['regional_arrival_mean'] = 0.0

    return df
