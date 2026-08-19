import json
import os
import pandas as pd
import numpy as np

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "crop_weather_windows.json")

def load_crop_weather_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def build_weather_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Builds weather features:
    - Base variables: temperature_max, temperature_min, precipitation, humidity, wind_speed, weather_code
    - Rolling metrics: rainfall_3d, rainfall_7d, rainfall_14d, rainfall_30d, temperature_mean_7d, humidity_mean_7d
    - Agricultural event flags: heavy_rain_flag, heat_stress_flag, cold_stress_flag, dry_spell_flag
    - Crop-specific lookback windows (short, medium, long)
    - Metadata flags: weather_missing, weather_data_type
    """
    df = df.copy()
    crop_configs = load_crop_weather_config()

    # Fill default baseline weather if not joined
    weather_cols = ['temperature_max', 'temperature_min', 'precipitation', 'humidity', 'wind_speed', 'weather_code']
    for c in weather_cols:
        if c not in df.columns:
            df[c] = np.nan

    df['weather_missing'] = df['temperature_max'].isna().astype(int)
    
    # Impute missing weather with seasonal defaults
    df['temp_max_clean'] = df['temperature_max'].fillna(32.0)
    df['temp_min_clean'] = df['temperature_min'].fillna(22.0)
    df['temp_mean_clean'] = (df['temp_max_clean'] + df['temp_min_clean']) / 2.0
    df['precip_clean'] = df['precipitation'].fillna(0.0)
    df['humidity_clean'] = df['humidity'].fillna(65.0)
    df['wind_clean'] = df['wind_speed'].fillna(10.0)

    # Rolling weather per market
    grouped_mkt = df.groupby('market')

    # Rolling rainfall
    for window in [3, 7, 14, 30]:
        df[f'rainfall_{window}d'] = grouped_mkt['precip_clean'].transform(
            lambda x: x.shift(1).rolling(window, min_periods=1).sum()
        ).fillna(0.0)

    # Rolling temperatures and humidity
    df['temperature_mean_7d'] = grouped_mkt['temp_mean_clean'].transform(
        lambda x: x.shift(1).rolling(7, min_periods=1).mean()
    ).fillna(27.0)

    df['humidity_mean_7d'] = grouped_mkt['humidity_clean'].transform(
        lambda x: x.shift(1).rolling(7, min_periods=1).mean()
    ).fillna(65.0)

    df['wind_mean_7d'] = grouped_mkt['wind_clean'].transform(
        lambda x: x.shift(1).rolling(7, min_periods=1).mean()
    ).fillna(10.0)

    # Event Flags
    df['heavy_rain_flag'] = (df['rainfall_3d'] >= 25.0).astype(int)
    df['heat_stress_flag'] = (df['temp_max_clean'] >= 38.0).astype(int)
    df['cold_stress_flag'] = (df['temp_min_clean'] <= 12.0).astype(int)
    df['dry_spell_flag'] = (df['rainfall_14d'] == 0.0).astype(int)

    # Crop-specific lookback windows
    df['crop_short_rainfall'] = df['rainfall_7d']
    df['crop_medium_rainfall'] = df['rainfall_14d']
    df['crop_long_rainfall'] = df['rainfall_30d']

    return df
