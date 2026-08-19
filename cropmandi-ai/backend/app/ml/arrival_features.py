import pandas as pd
import numpy as np

def build_arrival_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates arrival quantity features strictly using historical data (t <= 0):
    - arrival_quantity_lag_1, 2, 3, 7, 14, 28
    - arrival_change_1, 7, arrival_pct_change_1
    - arrival_rolling_mean_3, 7, 14, 28, arrival_rolling_std_7
    - arrival_vs_7_day_average, arrival_vs_28_day_average, arrival_zscore_28
    - arrival_pressure (ratio of latest arrival vs historical rolling average)
    - arrival_missing, arrival_imputed, arrival_imputation_age_days
    """
    df = df.copy()
    grouped = df.groupby(['market', 'commodity'])

    # 1. Missingness & Imputation Tracking
    df['arrival_missing'] = df['arrival_quantity'].isna().astype(int)
    
    # Calculate group rolling median for safe backward imputation within train data
    group_median = grouped['arrival_quantity'].transform(lambda x: x.shift(1).rolling(28, min_periods=1).median())
    df['arrival_quantity_imputed'] = df['arrival_quantity'].fillna(group_median).fillna(0.0)
    df['arrival_imputed'] = (df['arrival_missing'] == 1).astype(int)

    # Calculate days since last observation
    def get_gap_series(s):
        mask = s.notna()
        idx = pd.Series(np.where(mask, s.index, np.nan), index=s.index).ffill()
        return s.index - idx

    df['days_since_last_arrival_observation'] = grouped['arrival_quantity'].transform(get_gap_series).fillna(0)
    df['arrival_imputation_age_days'] = np.where(df['arrival_imputed'] == 1, df['days_since_last_arrival_observation'], 0)

    # 2. Lags for arrival quantity (strictly shifted <= t)
    for lag in [1, 2, 3, 7, 14, 28]:
        df[f'arrival_quantity_lag_{lag}'] = grouped['arrival_quantity_imputed'].shift(lag).fillna(0.0)

    # 3. Differences & percentage changes
    df['arrival_change_1'] = df['arrival_quantity_lag_1'] - df['arrival_quantity_lag_2']
    df['arrival_change_7'] = df['arrival_quantity_lag_1'] - df['arrival_quantity_lag_7']
    df['arrival_pct_change_1'] = df['arrival_change_1'] / (df['arrival_quantity_lag_2'] + 1.0)

    # 4. Rolling Statistics (Shifted by 1 to strictly prevent leakage)
    for window in [3, 7, 14, 28]:
        df[f'arrival_rolling_mean_{window}'] = grouped['arrival_quantity_imputed'].transform(
            lambda x: x.shift(1).rolling(window, min_periods=1).mean()
        ).fillna(0.0)

    df['arrival_rolling_std_7'] = grouped['arrival_quantity_imputed'].transform(
        lambda x: x.shift(1).rolling(7, min_periods=1).std()
    ).fillna(0.0)

    # 5. Supply Pressure & Comparison Ratios
    df['arrival_vs_7_day_average'] = df['arrival_quantity_lag_1'] - df['arrival_rolling_mean_7']
    df['arrival_vs_28_day_average'] = df['arrival_quantity_lag_1'] - df['arrival_rolling_mean_28']
    
    std28 = grouped['arrival_quantity_imputed'].transform(
        lambda x: x.shift(1).rolling(28, min_periods=1).std()
    ).fillna(1.0) + 1e-5
    df['arrival_zscore_28'] = (df['arrival_quantity_lag_1'] - df['arrival_rolling_mean_28']) / std28
    
    # Supply pressure: ratio of latest arrival vs rolling 28-day arrival average
    df['arrival_pressure'] = df['arrival_quantity_lag_1'] / (df['arrival_rolling_mean_28'] + 1.0)

    return df
