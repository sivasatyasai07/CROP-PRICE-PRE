import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from typing import Dict, Any

class NaiveBaseline:
    def predict(self, df: pd.DataFrame, horizon: int = 1) -> np.ndarray:
        return df['lag_1'].values

class MovingAverageBaseline:
    def __init__(self, window: int = 3):
        self.window = window

    def predict(self, df: pd.DataFrame, horizon: int = 1) -> np.ndarray:
        col = f'rolling_mean_{self.window}'
        if col in df.columns:
            return df[col].fillna(df['lag_1']).values
        return df['lag_1'].values

class SeasonalNaiveBaseline:
    def __init__(self, season_lag: int = 7):
        self.season_lag = season_lag

    def predict(self, df: pd.DataFrame, horizon: int = 1) -> np.ndarray:
        col = f'lag_{self.season_lag}'
        if col in df.columns:
            return df[col].fillna(df['lag_1']).values
        return df['lag_1'].values

class LinearRegressionBaseline:
    def __init__(self):
        self.model = LinearRegression()
        self.feature_cols = ['lag_1', 'lag_2', 'lag_3', 'lag_7', 'rolling_mean_7', 'rolling_mean_28']

    def fit(self, X: pd.DataFrame, y: np.array):
        X_clean = X[self.feature_cols].fillna(0)
        self.model.fit(X_clean, y)

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        X_clean = df[self.feature_cols].fillna(0)
        return self.model.predict(X_clean)
