"""
Temporal & Calendar Feature Engineering for Demand Forecasting.
Extracts cyclical and categorical time components without lookahead bias.
"""

import numpy as np
import pandas as pd


class TemporalFeatureBuilder:
    """
    Builds temporal and calendar features from a date column.
    """

    def __init__(self, date_col: str = "demand_date"):
        self.date_col = date_col

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extracts calendar and cyclical features from the DataFrame.
        
        Args:
            df: Input DataFrame containing the date_col.
            
        Returns:
            DataFrame with enriched temporal features.
        """
        df = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df[self.date_col]):
            df[self.date_col] = pd.to_datetime(df[self.date_col])

        dates = df[self.date_col]

        # Basic calendar features
        df["day_of_week"] = dates.dt.dayofweek
        df["day_of_month"] = dates.dt.day
        df["week_of_year"] = dates.dt.isocalendar().week.astype(int)
        df["month"] = dates.dt.month
        df["quarter"] = dates.dt.quarter
        df["year"] = dates.dt.year
        df["day_of_year"] = dates.dt.dayofyear

        # Binary indicator flags
        df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
        df["is_month_start"] = dates.dt.is_month_start.astype(int)
        df["is_month_end"] = dates.dt.is_month_end.astype(int)

        # Cyclical transforms (captures seamless transitions e.g. Sunday -> Monday, Dec -> Jan)
        df["sin_day_of_week"] = np.sin(2 * np.pi * df["day_of_week"] / 7.0)
        df["cos_day_of_week"] = np.cos(2 * np.pi * df["day_of_week"] / 7.0)
        df["sin_month"] = np.sin(2 * np.pi * (df["month"] - 1) / 12.0)
        df["cos_month"] = np.cos(2 * np.pi * (df["month"] - 1) / 12.0)

        return df
