import json
import os
import pandas as pd
import numpy as np

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "crop_season_config.json")

def load_season_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "monsoon": {"start_month": 6, "end_month": 9},
        "summer": {"start_month": 3, "end_month": 5},
        "winter": {"start_month": 10, "end_month": 2},
        "same_season_lookback_days": 7
    }

def build_seasonal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates calendar and seasonal features:
    - year, month, day, day_of_week, day_of_year, week_of_year, quarter
    - is_weekend, is_month_start, is_month_end, days_to_month_end
    - monsoon_flag, summer_flag, winter_flag
    - cyclical encodings: sin/cos for day_of_year, month, week_of_year, day_of_week
    - previous-year same-season lookback features (price_same_date_last_year, price_change_from_last_year)
    """
    df = df.copy()
    config = load_season_config()
    obs_date = pd.to_datetime(df['observation_date'])

    # 1. Calendar Components
    df['year'] = obs_date.dt.year
    df['month'] = obs_date.dt.month
    df['day'] = obs_date.dt.day
    df['day_of_week'] = obs_date.dt.dayofweek
    df['day_of_year'] = obs_date.dt.dayofyear
    df['week_of_year'] = obs_date.dt.isocalendar().week.astype(int)
    df['quarter'] = obs_date.dt.quarter

    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    df['is_month_start'] = obs_date.dt.is_month_start.astype(int)
    df['is_month_end'] = obs_date.dt.is_month_end.astype(int)
    df['days_to_month_end'] = (obs_date.dt.days_in_month - df['day']).astype(int)

    # 2. Agricultural Season Flags
    monsoon_m = config.get("monsoon", {"start_month": 6, "end_month": 9})
    summer_m = config.get("summer", {"start_month": 3, "end_month": 5})
    
    df['monsoon_flag'] = df['month'].between(monsoon_m["start_month"], monsoon_m["end_month"]).astype(int)
    df['summer_flag'] = df['month'].between(summer_m["start_month"], summer_m["end_month"]).astype(int)
    df['winter_flag'] = ((df['month'] >= 10) | (df['month'] <= 2)).astype(int)

    # 3. Cyclical Encodings
    df['sin_day_of_year'] = np.sin(2 * np.pi * df['day_of_year'] / 365.25)
    df['cos_day_of_year'] = np.cos(2 * np.pi * df['day_of_year'] / 365.25)
    df['sin_month'] = np.sin(2 * np.pi * df['month'] / 12.0)
    df['cos_month'] = np.cos(2 * np.pi * df['month'] / 12.0)
    df['sin_week_of_year'] = np.sin(2 * np.pi * df['week_of_year'] / 52.0)
    df['cos_week_of_year'] = np.cos(2 * np.pi * df['week_of_year'] / 52.0)
    df['sin_day_of_week'] = np.sin(2 * np.pi * df['day_of_week'] / 7.0)
    df['cos_day_of_week'] = np.cos(2 * np.pi * df['day_of_week'] / 7.0)

    # 4. Same-Season Previous-Year Price Features
    # Shift by ~365 days within (market, commodity)
    grouped = df.groupby(['market', 'commodity'])
    
    # Lag 365 days if present, else rolling 30-day month mean from previous year
    df['modal_price_lag_365'] = grouped['modal_price'].shift(365).ffill(limit=7).fillna(0.0)
    df['price_change_from_last_year'] = np.where(df['modal_price_lag_365'] > 0, df['modal_price'] - df['modal_price_lag_365'], 0.0)
    df['price_ratio_to_last_year'] = np.where(df['modal_price_lag_365'] > 0, df['modal_price'] / (df['modal_price_lag_365'] + 1e-5), 1.0)
    df['seasonal_reference_available'] = (df['modal_price_lag_365'] > 0).astype(int)

    return df
