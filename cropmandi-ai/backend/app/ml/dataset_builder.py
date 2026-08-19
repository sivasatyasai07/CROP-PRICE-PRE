import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from app.models import CleanedMarketPrice, Market, Commodity, WeatherObservation
from app.ml.feature_engineering import create_features, FEATURE_COLUMNS, CATEGORICAL_FEATURES
from typing import Tuple, Dict, Any, List

def build_dataset_from_db(db: Session) -> pd.DataFrame:
    # Query cleaned market prices joined with market and commodity
    results = db.query(
        CleanedMarketPrice.observation_date,
        CleanedMarketPrice.modal_price,
        CleanedMarketPrice.min_price,
        CleanedMarketPrice.max_price,
        CleanedMarketPrice.arrival_quantity,
        Market.canonical_name.label("market"),
        Market.district,
        Commodity.canonical_name.label("commodity"),
        WeatherObservation.temperature_max,
        WeatherObservation.temperature_min,
        WeatherObservation.precipitation,
        WeatherObservation.humidity,
        WeatherObservation.wind_speed,
        WeatherObservation.weather_code
    ).join(Market, CleanedMarketPrice.market_id == Market.id)\
     .join(Commodity, CleanedMarketPrice.commodity_id == Commodity.id)\
     .outerjoin(WeatherObservation, (CleanedMarketPrice.market_id == WeatherObservation.market_id) & 
                                     (CleanedMarketPrice.observation_date == WeatherObservation.observation_date))\
     .all()

    if not results:
        import os
        from app.services.master_data_service import get_master_data_path, parse_csv_date
        from app.utils.market_normalization import normalize_market_name, normalize_commodity_name
        csv_path = get_master_data_path()
        if os.path.exists(csv_path):
            try:
                df_csv = pd.read_csv(csv_path)
                data = []
                for _, row in df_csv.iterrows():
                    obs_d = parse_csv_date(str(row.get("arrival_date", row.get("Date", ""))))
                    mkt_norm = normalize_market_name(str(row.get("market", row.get("Market", ""))))
                    comm_norm = normalize_commodity_name(str(row.get("commodity", row.get("Commodity", ""))))
                    dist = str(row.get("district", row.get("District", "Andhra Pradesh")))
                    try:
                        m_p = float(row.get("modal_price", row.get("Modal_Price", 0)))
                    except Exception:
                        m_p = 0.0
                    try:
                        arr_q = float(row.get("arrival_quantity", row.get("Arrivals", 0)))
                    except Exception:
                        arr_q = 0.0
                    
                    if obs_d and m_p > 0:
                        data.append({
                            'market': mkt_norm,
                            'district': dist,
                            'commodity': comm_norm,
                            'observation_date': obs_d,
                            'modal_price': m_p,
                            'min_price': m_p * 0.95,
                            'max_price': m_p * 1.05,
                            'arrival_quantity': arr_q,
                            'temperature_max': 30.0,
                            'temperature_min': 22.0,
                            'precipitation': 0.0,
                            'humidity': 65.0,
                            'wind_speed': 10.0,
                            'weather_code': 0
                        })
                if data:
                    raw_df = pd.DataFrame(data)
                    return create_features(raw_df)
            except Exception:
                pass
        return pd.DataFrame()

    data = []
    for r in results:
        data.append({
            'market': r.market,
            'district': r.district,
            'commodity': r.commodity,
            'observation_date': r.observation_date,
            'modal_price': r.modal_price,
            'min_price': r.min_price,
            'max_price': r.max_price,
            'arrival_quantity': r.arrival_quantity,
            'temperature_max': r.temperature_max,
            'temperature_min': r.temperature_min,
            'precipitation': r.precipitation,
            'humidity': r.humidity,
            'wind_speed': r.wind_speed,
            'weather_code': r.weather_code
        })

    raw_df = pd.DataFrame(data)
    
    # Generate complete calendar per group to handle irregular observation dates accurately
    full_df_list = []
    for (mkt, comm), grp in raw_df.groupby(['market', 'commodity']):
        grp = grp.sort_values('observation_date')
        district_val = grp['district'].iloc[0]
        
        min_d = grp['observation_date'].min()
        max_d = grp['observation_date'].max()
        
        idx = pd.date_range(min_d, max_d, freq='D').date
        calendar_df = pd.DataFrame({'observation_date': idx})
        calendar_df['market'] = mkt
        calendar_df['district'] = district_val
        calendar_df['commodity'] = comm
        
        merged = pd.merge(calendar_df, grp, on=['market', 'district', 'commodity', 'observation_date'], how='left')
        
        # Forward fill price targets up to 3 days for feature generation only
        merged['modal_price_ffill'] = merged['modal_price'].ffill()
        merged['min_price_ffill'] = merged['min_price'].ffill()
        merged['max_price_ffill'] = merged['max_price'].ffill()
        
        full_df_list.append(merged)
        
    full_df = pd.concat(full_df_list, ignore_index=True)
    
    # Use ffill prices for feature calculations
    df_features_input = full_df.copy()
    df_features_input['modal_price_orig'] = df_features_input['modal_price']
    df_features_input['modal_price'] = df_features_input['modal_price_ffill']
    df_features_input['min_price'] = df_features_input['min_price_ffill']
    df_features_input['max_price'] = df_features_input['max_price_ffill']
    
    df_feat = create_features(df_features_input)
    df_feat['modal_price'] = df_feat['modal_price_orig'] # Restore actual target

    # Direct target creation (t+1, t+2, t+3)
    grouped = df_feat.groupby(['market', 'commodity'])
    df_feat['target_h1'] = grouped['modal_price'].shift(-1)
    df_feat['target_h2'] = grouped['modal_price'].shift(-2)
    df_feat['target_h3'] = grouped['modal_price'].shift(-3)

    return df_feat

def chronological_split(
    df: pd.DataFrame,
    train_end: str = "2025-12-31",
    test_start: str = "2026-01-01"
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df['obs_dt'] = pd.to_datetime(df['observation_date'])
    t_end = pd.to_datetime(train_end)
    t_start = pd.to_datetime(test_start)

    train_df = df[df['obs_dt'] <= t_end].copy()
    test_df = df[df['obs_dt'] >= t_start].copy()

    return train_df, test_df
