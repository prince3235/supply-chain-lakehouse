"""
Statistical & Heuristic Demand Forecasting Baselines.
Serves as benchmark threshold for comparing candidate ML models.
"""

from typing import Optional, Union
import numpy as np
import pandas as pd


class NaivePreviousDayBaseline:
    """
    Naive baseline that predicts tomorrow's demand as today's demand (lag_1).
    """

    def __init__(self, lag_col: str = "lag_1"):
        self.lag_col = lag_col
        self.default_fallback: float = 0.0

    def fit(self, X: pd.DataFrame, y: Union[np.ndarray, pd.Series]) -> "NaivePreviousDayBaseline":
        self.default_fallback = float(np.mean(y)) if len(y) > 0 else 0.0
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self.lag_col in X.columns:
            return np.maximum(X[self.lag_col].fillna(self.default_fallback).to_numpy(), 0.0)
        return np.full(len(X), self.default_fallback)


class MovingAverageBaseline:
    """
    7-Day Moving Average baseline for demand forecasting.
    """

    def __init__(self, rolling_col: str = "rolling_mean_7", window: int = 7):
        self.rolling_col = rolling_col
        self.window = window
        self.default_fallback: float = 0.0

    def fit(self, X: pd.DataFrame, y: Union[np.ndarray, pd.Series]) -> "MovingAverageBaseline":
        self.default_fallback = float(np.mean(y)) if len(y) > 0 else 0.0
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self.rolling_col in X.columns:
            return np.maximum(X[self.rolling_col].fillna(self.default_fallback).to_numpy(), 0.0)
        return np.full(len(X), self.default_fallback)
