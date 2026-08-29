"""
End-to-End Feature Engineering Pipeline for Supply Chain Demand Forecasting.
Integrates gold datasets and executes reproducible feature extraction.
"""

from typing import List, Optional, Tuple, Dict, Any
import pandas as pd
import numpy as np

from src.features.historical import HistoricalFeatureBuilder
from src.features.temporal import TemporalFeatureBuilder
from src.features.pricing_inventory import PricingInventoryFeatureBuilder


class FeaturePipeline:
    """
    Orchestrates end-to-end feature extraction from Gold-layer tables to an ML feature matrix.
    """

    DEFAULT_FEATURE_COLUMNS = [
        # Temporal
        "day_of_week",
        "day_of_month",
        "week_of_year",
        "month",
        "quarter",
        "is_weekend",
        "is_month_start",
        "is_month_end",
        "sin_day_of_week",
        "cos_day_of_week",
        "sin_month",
        "cos_month",
        # Historical Lags
        "lag_1",
        "lag_2",
        "lag_3",
        "lag_7",
        "lag_14",
        "lag_21",
        "lag_30",
        # Rolling Statistics
        "rolling_mean_7",
        "rolling_std_7",
        "rolling_min_7",
        "rolling_max_7",
        "rolling_mean_14",
        "rolling_std_14",
        "rolling_mean_30",
        "rolling_std_30",
        # Trend & Momentum
        "demand_ratio_7_vs_30",
        "demand_growth_wow",
        "demand_volatility_30",
        # Pricing & Inventory
        "unit_price",
        "discount_percentage",
        "is_discounted",
        "is_stockout",
        "is_near_stockout",
        "inventory_to_safety_ratio",
        "inventory_coverage_days",
    ]

    def __init__(
        self,
        date_col: str = "demand_date",
        target_col: str = "daily_demand",
        entity_cols: Optional[List[str]] = None,
        feature_cols: Optional[List[str]] = None,
    ):
        self.date_col = date_col
        self.target_col = target_col
        self.entity_cols = entity_cols or ["product_id", "store_id"]
        self.feature_cols = feature_cols or self.DEFAULT_FEATURE_COLUMNS

        self.temporal_builder = TemporalFeatureBuilder(date_col=self.date_col)
        self.historical_builder = HistoricalFeatureBuilder(
            group_cols=self.entity_cols,
            date_col=self.date_col,
            target_col=self.target_col,
        )
        self.pricing_inventory_builder = PricingInventoryFeatureBuilder()

    def build_features(
        self,
        demand_df: pd.DataFrame,
        products_df: Optional[pd.DataFrame] = None,
        inventory_df: Optional[pd.DataFrame] = None,
        fill_na: bool = True,
    ) -> pd.DataFrame:
        """
        Executes feature transformation pipeline on input datasets.
        
        Args:
            demand_df: Daily demand table (product_id, store_id, demand_date, daily_demand)
            products_df: Optional product dimension metadata (product_id, category, unit_price)
            inventory_df: Optional inventory health dataset (product_id, store_id, snapshot_date, total_available, current_safety_stock)
            fill_na: If True, fills lag-induced initial NaNs with deterministic fallbacks.
            
        Returns:
            Fully transformed feature DataFrame.
        """
        df = demand_df.copy()
        
        # Ensure column standard naming
        if "total_daily_quantity" in df.columns and self.target_col not in df.columns:
            df[self.target_col] = df["total_daily_quantity"]

        # Merge Product Metadata if provided
        if products_df is not None and "product_id" in products_df.columns:
            join_cols = [c for c in ["product_id", "category", "unit_price"] if c in products_df.columns]
            df = df.merge(products_df[join_cols], on="product_id", how="left")
        elif "unit_price" not in df.columns:
            df["unit_price"] = 10.0  # Default fallback if unjoined

        # Merge Inventory Data if provided
        if inventory_df is not None and "snapshot_date" in inventory_df.columns:
            inv_copy = inventory_df.copy()
            inv_copy[self.date_col] = pd.to_datetime(inv_copy["snapshot_date"])
            merge_keys = [c for c in self.entity_cols if c in inv_copy.columns] + [self.date_col]
            inv_cols = [c for c in ["total_available", "current_safety_stock", "current_reorder_point"] if c in inv_copy.columns]
            df = df.merge(inv_copy[merge_keys + inv_cols], on=merge_keys, how="left")

        # Fallbacks for inventory metrics if missing
        if "total_available" not in df.columns:
            df["total_available"] = 100.0
        if "current_safety_stock" not in df.columns:
            df["current_safety_stock"] = 20.0

        # Execute Transformation Layers
        df = self.temporal_builder.transform(df)
        df = self.historical_builder.transform(df)
        df = self.pricing_inventory_builder.transform(df)

        if fill_na:
            # Handle lag warming period NaNs
            for col in df.columns:
                if col.startswith("lag_") or col.startswith("rolling_"):
                    # Fill with target median or 0
                    df[col] = df[col].fillna(0.0)
                elif df[col].dtype in [np.float64, np.float32, np.int64, np.int32]:
                    df[col] = df[col].fillna(0)

        return df

    def get_feature_matrix(
        self,
        df: pd.DataFrame,
    ) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
        """
        Splits transformed DataFrame into Feature Matrix X, Target Vector y, and Feature Name list.
        """
        available_features = [f for f in self.feature_cols if f in df.columns]
        X = df[available_features].copy()
        y = df[self.target_col].copy()
        return X, y, available_features
