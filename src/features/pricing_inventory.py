"""
Pricing & Inventory Health Feature Engineering.
Derives promotional elasticity, discount intensity, and stock health indicators.
"""

import pandas as pd
import numpy as np


class PricingInventoryFeatureBuilder:
    """
    Computes domain-specific pricing, promotional, and inventory balance features.
    """

    def __init__(
        self,
        price_col: str = "unit_price",
        discount_amount_col: str = "discount_amount",
        inventory_col: str = "total_available",
        safety_stock_col: str = "current_safety_stock",
    ):
        self.price_col = price_col
        self.discount_amount_col = discount_amount_col
        self.inventory_col = inventory_col
        self.safety_stock_col = safety_stock_col

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extracts pricing elasticity and inventory safety metrics.
        """
        df = df.copy()

        # Pricing & Promotion Features
        if self.price_col in df.columns:
            base_price = df[self.price_col].fillna(0.0)

            if self.discount_amount_col in df.columns:
                discount = df[self.discount_amount_col].fillna(0.0)
                original_price = base_price + discount
                df["discount_percentage"] = np.where(
                    original_price > 0,
                    (discount / original_price) * 100.0,
                    0.0
                )
                df["is_discounted"] = (discount > 0).astype(int)
            else:
                df["discount_percentage"] = 0.0
                df["is_discounted"] = 0

        # Inventory Health & Buffer Ratios
        if self.inventory_col in df.columns:
            inv = df[self.inventory_col].fillna(0.0)
            df["is_stockout"] = (inv <= 0).astype(int)

            if self.safety_stock_col in df.columns:
                safety = df[self.safety_stock_col].fillna(1.0)
                df["inventory_to_safety_ratio"] = (inv / (safety + 1e-5)).clip(0.0, 50.0)
                df["is_near_stockout"] = (inv <= safety).astype(int)

            if "rolling_mean_7" in df.columns:
                # Approximate days of forward coverage based on recent run-rate
                run_rate = df["rolling_mean_7"].fillna(1.0)
                df["inventory_coverage_days"] = (inv / (run_rate + 1e-5)).clip(0.0, 365.0)

        return df
