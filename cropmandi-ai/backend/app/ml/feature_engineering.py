import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Any, Optional

from app.ml.arrival_features import build_arrival_features
from app.ml.seasonal_features import build_seasonal_features
from app.ml.cross_market_features import build_cross_market_features
from app.ml.weather_features import build_weather_features
from app.ml.target_builder import build_direct_horizon_targets

CATEGORICAL_FEATURES = ['market', 'commodity', 'district']

PRICE_FEATURE_COLUMNS = [
    'lag_1', 'lag_2', 'lag_3', 'lag_7', 'lag_14', 'lag_21', 'lag_28',
    'rolling_mean_3', 'rolling_mean_7', 'rolling_mean_14', 'rolling_mean_28',
    'rolling_median_7', 'rolling_min_7', 'rolling_max_7',
    'rolling_std_7', 'rolling_std_14', 'rolling_std_28',
    'price_change_1', 'price_change_3', 'price_change_7',
    'price_percentage_change_1', 'price_percentage_change_7',
    'price_vs_7_day_average', 'price_vs_28_day_average',
    'price_range', 'price_range_percentage', 'modal_position'
]

SEASONAL_FEATURE_COLUMNS = [
    'year', 'month', 'day_of_week', 'day_of_year', 'is_weekend', 'quarter',
    'sin_month', 'cos_month', 'sin_day_of_year', 'cos_day_of_year',
    'sin_day_of_week', 'cos_day_of_week', 'monsoon_flag', 'summer_flag', 'winter_flag',
    'modal_price_lag_365', 'price_change_from_last_year', 'price_ratio_to_last_year', 'seasonal_reference_available'
]

ARRIVAL_FEATURE_COLUMNS = [
    'arrival_missing', 'arrival_imputed', 'arrival_quantity_lag_1', 'arrival_quantity_lag_2',
    'arrival_quantity_lag_3', 'arrival_quantity_lag_7', 'arrival_quantity_lag_14',
    'arrival_change_1', 'arrival_change_7', 'arrival_pct_change_1',
    'arrival_rolling_mean_3', 'arrival_rolling_mean_7', 'arrival_rolling_mean_14', 'arrival_rolling_mean_28',
    'arrival_vs_7_day_average', 'arrival_vs_28_day_average', 'arrival_pressure', 'arrival_zscore_28'
]

CROSS_MARKET_FEATURE_COLUMNS = [
    'same_day_regional_mean', 'same_day_regional_median', 'same_day_regional_min', 'same_day_regional_max',
    'same_day_regional_std', 'market_price_minus_regional_mean', 'market_price_ratio_to_regional_mean',
    'number_of_markets_reporting', 'regional_arrival_total', 'regional_arrival_mean'
]

WEATHER_FEATURE_COLUMNS = [
    'weather_missing', 'temp_max_clean', 'temp_min_clean', 'temp_mean_clean', 'precip_clean', 'humidity_clean', 'wind_clean',
    'rainfall_3d', 'rainfall_7d', 'rainfall_14d', 'rainfall_30d',
    'temperature_mean_7d', 'humidity_mean_7d', 'wind_mean_7d',
    'heavy_rain_flag', 'heat_stress_flag', 'cold_stress_flag', 'dry_spell_flag',
    'crop_short_rainfall', 'crop_medium_rainfall', 'crop_long_rainfall'
]

FEATURE_COLUMNS = [
    'market', 'commodity', 'district', 'year', 'month', 'day_of_week', 'day_of_year', 'is_weekend', 'quarter',
    'sin_month', 'cos_month', 'sin_day_of_year', 'cos_day_of_year', 'sin_day_of_week', 'cos_day_of_week',
    'monsoon_flag', 'summer_flag', 'winter_flag', 'price_range', 'price_range_percentage', 'modal_position',
    'lag_1', 'lag_2', 'lag_3', 'lag_7', 'lag_14', 'lag_21', 'lag_28', 'rolling_mean_3', 'rolling_mean_7',
    'rolling_mean_14', 'rolling_mean_28', 'rolling_median_7', 'rolling_min_7', 'rolling_max_7', 'rolling_std_7',
    'rolling_std_14', 'rolling_std_28', 'price_change_1', 'price_change_3', 'price_change_7',
    'price_percentage_change_1', 'price_percentage_change_7', 'price_vs_7_day_average', 'price_vs_28_day_average',
    'modal_price_lag_365', 'price_change_from_last_year', 'price_ratio_to_last_year', 'seasonal_reference_available',
    'arrival_missing', 'arrival_imputed', 'arrival_quantity_lag_1', 'arrival_quantity_lag_2', 'arrival_quantity_lag_3',
    'arrival_quantity_lag_7', 'arrival_quantity_lag_14', 'arrival_change_1', 'arrival_change_7', 'arrival_pct_change_1',
    'arrival_rolling_mean_3', 'arrival_rolling_mean_7', 'arrival_rolling_mean_14', 'arrival_rolling_mean_28',
    'arrival_vs_7_day_average', 'arrival_vs_28_day_average', 'arrival_pressure', 'arrival_zscore_28',
    'same_day_regional_mean', 'same_day_regional_median', 'same_day_regional_min', 'same_day_regional_max',
    'same_day_regional_std', 'market_price_minus_regional_mean', 'market_price_ratio_to_regional_mean',
    'number_of_markets_reporting', 'regional_arrival_total', 'regional_arrival_mean', 'weather_missing',
    'temp_max_clean', 'temp_min_clean', 'temp_mean_clean', 'precip_clean', 'humidity_clean', 'wind_clean',
    'rainfall_3d', 'rainfall_7d', 'rainfall_14d', 'rainfall_30d', 'temperature_mean_7d', 'humidity_mean_7d',
    'wind_mean_7d', 'heavy_rain_flag', 'heat_stress_flag', 'cold_stress_flag', 'dry_spell_flag',
    'crop_short_rainfall', 'crop_medium_rainfall', 'crop_long_rainfall'
]

NUMERIC_FEATURES = [c for c in FEATURE_COLUMNS if c not in CATEGORICAL_FEATURES]

def get_feature_columns() -> List[str]:
    return list(FEATURE_COLUMNS)

def get_categorical_columns() -> List[str]:
    return list(CATEGORICAL_FEATURES)

def get_numeric_columns() -> List[str]:
    return list(NUMERIC_FEATURES)

def create_features(df: pd.DataFrame, is_training: bool = True) -> pd.DataFrame:
    """
    Creates comprehensive leak-free feature matrix from input market observations.
    All rolling and lag statistics are strictly shifted <= t-1.
    """
    df = df.copy()
    if 'observation_date' in df.columns:
        df['observation_date'] = pd.to_datetime(df['observation_date'])
        df = df.sort_values(by=['market', 'commodity', 'observation_date']).reset_index(drop=True)

    # 1. Targets (if training)
    if is_training:
        df = build_direct_horizon_targets(df, horizons=[1, 2, 3])

    # 2. Base price range
    df['min_price'] = df['min_price'].fillna(df['modal_price'])
    df['max_price'] = df['max_price'].fillna(df['modal_price'])
    df['price_range'] = df['max_price'] - df['min_price']
    df['price_range_percentage'] = df['price_range'] / (df['modal_price'] + 1e-5)
    
    denom = df['max_price'] - df['min_price']
    df['modal_position'] = np.where(denom > 0, (df['modal_price'] - df['min_price']) / denom, 0.5)

    # 3. Lags & rolling for modal_price (strictly shifted to prevent leakage)
    grouped = df.groupby(['market', 'commodity'])
    for lag in [1, 2, 3, 7, 14, 21, 28]:
        df[f'lag_{lag}'] = grouped['modal_price'].shift(lag).bfill().fillna(0.0)

    for window in [3, 7, 14, 28]:
        df[f'rolling_mean_{window}'] = grouped['modal_price'].transform(
            lambda x: x.shift(1).rolling(window, min_periods=1).mean()
        ).fillna(df['lag_1'])

    df['rolling_median_7'] = grouped['modal_price'].transform(lambda x: x.shift(1).rolling(7, min_periods=1).median()).fillna(df['lag_1'])
    df['rolling_min_7'] = grouped['modal_price'].transform(lambda x: x.shift(1).rolling(7, min_periods=1).min()).fillna(df['lag_1'])
    df['rolling_max_7'] = grouped['modal_price'].transform(lambda x: x.shift(1).rolling(7, min_periods=1).max()).fillna(df['lag_1'])

    for window in [7, 14, 28]:
        df[f'rolling_std_{window}'] = grouped['modal_price'].transform(lambda x: x.shift(1).rolling(window, min_periods=1).std()).fillna(0.0)

    df['price_change_1'] = df['lag_1'] - df['lag_2']
    df['price_change_3'] = df['lag_1'] - df['lag_3']
    df['price_change_7'] = df['lag_1'] - df['lag_7']
    df['price_percentage_change_1'] = df['price_change_1'] / (df['lag_2'] + 1e-5)
    df['price_percentage_change_7'] = df['price_change_7'] / (df['lag_7'] + 1e-5)
    
    df['price_vs_7_day_average'] = df['lag_1'] - df['rolling_mean_7']
    df['price_vs_28_day_average'] = df['lag_1'] - df['rolling_mean_28']

    # 4. Seasonal & Calendar features
    df = build_seasonal_features(df)

    # 5. Arrival features
    df = build_arrival_features(df)

    # 6. Cross-market features
    df = build_cross_market_features(df)

    # 7. Weather features
    df = build_weather_features(df)

    return df

def build_training_features(df: pd.DataFrame) -> pd.DataFrame:
    return create_features(df, is_training=True)

def build_inference_features(
    history: pd.DataFrame,
    commodity: str,
    market: str,
    forecast_origin: pd.Timestamp
) -> pd.DataFrame:
    """
    Extracts the leak-free single-row feature vector for runtime prediction strictly at or before forecast_origin.
    """
    df_feat = create_features(history, is_training=False)
    sub = df_feat[
        (df_feat['commodity'] == commodity) &
        (df_feat['market'] == market) &
        (pd.to_datetime(df_feat['observation_date']) <= forecast_origin)
    ].sort_values('observation_date')
    
    if sub.empty:
        raise ValueError(f"No historical records found for {commodity} in {market} on or before {forecast_origin.strftime('%Y-%m-%d')}")
        
    latest_row = sub.iloc[-1]
    cols = [c for c in FEATURE_COLUMNS if c in latest_row.index]
    row_df = pd.DataFrame([latest_row[cols]])
    
    for c in cols:
        if c in CATEGORICAL_FEATURES:
            row_df[c] = row_df[c].fillna("__MISSING__").astype(str)
        else:
            row_df[c] = row_df[c].fillna(0.0).astype(float)
            
    return row_df

def validate_feature_schema(X_pred: pd.DataFrame, expected_features: Optional[List[str]] = None) -> Tuple[bool, List[str], List[str]]:
    expected = expected_features or FEATURE_COLUMNS
    actual = list(X_pred.columns)
    missing = [f for f in expected if f not in actual]
    unexpected = [f for f in actual if f not in expected]
    is_valid = len(missing) == 0
    return is_valid, missing, unexpected
