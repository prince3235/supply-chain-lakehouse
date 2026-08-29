"""
Unit Tests for Feature Engineering Pipeline.
Validates temporal, lag, pricing, inventory features and verifies zero-leakage invariant.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.features.temporal import TemporalFeatureBuilder
from src.features.historical import HistoricalFeatureBuilder
from src.features.pricing_inventory import PricingInventoryFeatureBuilder
from src.features.pipeline import FeaturePipeline


@pytest.fixture
def sample_demand_series():
    """Generates 45 days of sequential daily demand for 2 product-store entities."""
    records = []
    base_date = datetime(2026, 1, 1)
    
    for entity in [("PROD_1", "STORE_1"), ("PROD_2", "STORE_1")]:
        p_id, s_id = entity
        for d in range(45):
            curr_date = base_date + timedelta(days=d)
            # Predictable linear + day pattern: 10 + d + (d % 7)
            demand = 10.0 + float(d) + float(d % 7)
            records.append({
                "product_id": p_id,
                "store_id": s_id,
                "demand_date": curr_date.strftime("%Y-%m-%d"),
                "daily_demand": demand,
                "unit_price": 25.0,
                "discount_amount": 2.5 if d % 5 == 0 else 0.0,
                "total_available": 100.0 - (d % 10) * 10.0,
                "current_safety_stock": 20.0,
            })
            
    return pd.DataFrame(records)


def test_temporal_feature_builder(sample_demand_series):
    builder = TemporalFeatureBuilder(date_col="demand_date")
    result = builder.transform(sample_demand_series)
    
    # Check expected columns exist
    expected_cols = [
        "day_of_week", "day_of_month", "week_of_year", "month",
        "quarter", "is_weekend", "sin_day_of_week", "cos_day_of_week"
    ]
    for col in expected_cols:
        assert col in result.columns, f"Missing temporal column: {col}"
        
    # Check day of week range
    assert result["day_of_week"].min() >= 0
    assert result["day_of_week"].max() <= 6
    assert set(result["is_weekend"].unique()).issubset({0, 1})


def test_historical_feature_builder(sample_demand_series):
    builder = HistoricalFeatureBuilder(
        group_cols=["product_id", "store_id"],
        date_col="demand_date",
        target_col="daily_demand",
        lags=[1, 7],
        rolling_windows=[7],
    )
    result = builder.transform(sample_demand_series)
    
    assert "lag_1" in result.columns
    assert "lag_7" in result.columns
    assert "rolling_mean_7" in result.columns
    
    # Filter for first entity and check lag value accuracy
    p1 = result[result["product_id"] == "PROD_1"].sort_values("demand_date").reset_index(drop=True)
    
    # Day 0 lag_1 should be NaN (no prior day)
    assert np.isnan(p1.loc[0, "lag_1"])
    # Day 1 lag_1 should equal Day 0 daily_demand
    assert p1.loc[1, "lag_1"] == p1.loc[0, "daily_demand"]
    # Day 7 lag_7 should equal Day 0 daily_demand
    assert p1.loc[7, "lag_7"] == p1.loc[0, "daily_demand"]


def test_zero_leakage_invariant(sample_demand_series):
    """
    CRITICAL TEST: Verifies that rolling features at day D strictly DO NOT include
    the daily_demand of day D.
    """
    builder = HistoricalFeatureBuilder(
        group_cols=["product_id", "store_id"],
        date_col="demand_date",
        target_col="daily_demand",
        lags=[1],
        rolling_windows=[7],
    )
    result = builder.transform(sample_demand_series)
    p1 = result[result["product_id"] == "PROD_1"].sort_values("demand_date").reset_index(drop=True)
    
    # Check Day 1 rolling_mean_7: Should equal mean of day 0 only (since rolling on shifted lag_1)
    day_0_demand = p1.loc[0, "daily_demand"]
    day_1_rolling_mean = p1.loc[1, "rolling_mean_7"]
    assert pytest.approx(day_1_rolling_mean, 0.001) == day_0_demand
    
    # Ensure current day demand wasn't included in Day 1 rolling calculation
    assert day_1_rolling_mean != p1.loc[1, "daily_demand"]


def test_pricing_inventory_builder(sample_demand_series):
    builder = PricingInventoryFeatureBuilder()
    result = builder.transform(sample_demand_series)
    
    assert "discount_percentage" in result.columns
    assert "is_discounted" in result.columns
    assert "is_stockout" in result.columns
    assert "inventory_to_safety_ratio" in result.columns
    
    # Check discount calculation (2.5 discount on 25 base price => 2.5 / 27.5 * 100 = 9.09%)
    discounted_rows = result[result["is_discounted"] == 1]
    assert len(discounted_rows) > 0
    assert (discounted_rows["discount_percentage"] > 0).all()


def test_full_feature_pipeline(sample_demand_series):
    pipeline = FeaturePipeline(
        date_col="demand_date",
        target_col="daily_demand",
        entity_cols=["product_id", "store_id"],
    )
    
    feature_df = pipeline.build_features(sample_demand_series, fill_na=True)
    
    assert len(feature_df) == len(sample_demand_series)
    # Check that fill_na removed NaNs from critical lag columns
    assert not feature_df["lag_1"].isna().any()
    assert not feature_df["rolling_mean_7"].isna().any()
    
    X, y, feature_names = pipeline.get_feature_matrix(feature_df)
    assert len(X) == len(sample_demand_series)
    assert len(y) == len(sample_demand_series)
    assert len(feature_names) > 15
