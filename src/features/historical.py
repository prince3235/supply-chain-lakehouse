"""
Historical Demand & Lag Feature Engineering.
Implements time-series lags and rolling statistics with strict zero-leakage constraints.
"""

from typing import List
import pandas as pd
import numpy as np


class HistoricalFeatureBuilder:
    """
    Computes time-series lag and rolling statistics for demand forecasting.
    Enforces zero future leakage: all rolling features are computed strictly on shifted data (t-1).
    """

    def __init__(
        self,
        group_cols: List[str] = None,
        date_col: str = "demand_date",
        target_col: str = "daily_demand",
        lags: List[int] = None,
        rolling_windows: List[int] = None,
    ):
        self.group_cols = group_cols or ["product_id", "store_id"]
        self.date_col = date_col
        self.target_col = target_col
        self.lags = lags or [1, 2, 3, 7, 14, 21, 30]
        self.rolling_windows = rolling_windows or [7, 14, 30]

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates lags and rolling window metrics per entity group.
        
        Args:
            df: Input DataFrame containing grouping columns, date, and target variable.
            
        Returns:
            DataFrame containing calculated historical features.
        """
        df = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df[self.date_col]):
            df[self.date_col] = pd.to_datetime(df[self.date_col])

        # Sort values chronologically within each group
        df = df.sort_values(by=self.group_cols + [self.date_col]).reset_index(drop=True)

        # 1. Compute discrete lags
        for lag in self.lags:
            col_name = f"lag_{lag}"
            df[col_name] = df.groupby(self.group_cols)[self.target_col].shift(lag)

        # 2. Compute rolling statistics strictly on lag_1 (prevents current date leakage)
        # Shifted series represents data strictly known as of day D-1
        shifted_demand = df.groupby(self.group_cols)[self.target_col].shift(1)

        for window in self.rolling_windows:
            grouped = shifted_demand.groupby([df[c] for c in self.group_cols])
            
            df[f"rolling_mean_{window}"] = grouped.transform(
                lambda s: s.rolling(window=window, min_periods=1).mean()
            )
            df[f"rolling_std_{window}"] = grouped.transform(
                lambda s: s.rolling(window=window, min_periods=1).std().fillna(0.0)
            )
            df[f"rolling_min_{window}"] = grouped.transform(
                lambda s: s.rolling(window=window, min_periods=1).min()
            )
            df[f"rolling_max_{window}"] = grouped.transform(
                lambda s: s.rolling(window=window, min_periods=1).max()
            )

        # 3. Demand momentum & trend ratios
        if 7 in self.rolling_windows and 30 in self.rolling_windows:
            df["demand_ratio_7_vs_30"] = (
                df["rolling_mean_7"] / (df["rolling_mean_30"] + 1e-5)
            ).clip(0.0, 10.0)

        if 1 in self.lags and 7 in self.lags:
            df["demand_growth_wow"] = (
                (df["lag_1"] - df["lag_7"]) / (df["lag_7"] + 1.0)
            ).clip(-5.0, 5.0)

        if "rolling_std_30" in df.columns and "rolling_mean_30" in df.columns:
            df["demand_volatility_30"] = (
                df["rolling_std_30"] / (df["rolling_mean_30"] + 1e-5)
            ).clip(0.0, 10.0)

        return df
