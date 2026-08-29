"""
Unit Tests for Batch Inference, Inventory Recommendation, and Anomaly Detection.
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from src.features.pipeline import FeaturePipeline
from src.training.models import DemandForecaster
from src.inference.batch_predict import BatchInferenceEngine
from src.inference.inventory_recommender import (
    InventoryRecommendationEngine,
    StockoutUrgency,
)
from src.inference.anomaly_detector import SupplyChainAnomalyDetector


@pytest.fixture
def sample_history_and_model():
    records = []
    base_date = datetime(2026, 1, 1)
    for d in range(40):
        curr_date = base_date + timedelta(days=d)
        records.append({
            "product_id": "P100",
            "store_id": "S200",
            "demand_date": curr_date.strftime("%Y-%m-%d"),
            "daily_demand": 25.0 + (d % 5),
            "unit_price": 40.0,
            "total_available": 100.0,
            "current_safety_stock": 20.0,
        })
    df = pd.DataFrame(records)
    pipeline = FeaturePipeline()
    feature_df = pipeline.build_features(df)
    X, y, feature_names = pipeline.get_feature_matrix(feature_df)
    
    model = DemandForecaster(model_type="random_forest", feature_names=feature_names)
    model.fit(X, y)
    return df, model, pipeline


def test_batch_inference_engine(sample_history_and_model):
    df, model, pipeline = sample_history_and_model
    engine = BatchInferenceEngine(model_obj=model, feature_pipeline=pipeline)
    
    forecast_df = engine.generate_forecasts(historical_df=df, horizon_days=7)
    
    assert len(forecast_df) == 7
    expected_cols = [
        "product_id", "store_id", "forecast_date", "horizon_step",
        "predicted_demand", "confidence_lower", "confidence_upper", "model_version"
    ]
    for col in expected_cols:
        assert col in forecast_df.columns
        
    # Check predictions are non-negative and lower <= upper
    assert (forecast_df["predicted_demand"] >= 0).all()
    assert (forecast_df["confidence_lower"] <= forecast_df["confidence_upper"]).all()


def test_dynamic_safety_stock_calculation():
    engine = InventoryRecommendationEngine()
    
    # Predictable demand (std = 1.0), low lead time (3 days)
    ss_low = engine.calculate_dynamic_safety_stock(
        daily_demand_mean=20.0,
        daily_demand_std=1.0,
        lead_time_days=3.0,
        lead_time_std=0.5,
        service_level=95.0,
    )
    
    # Volatile demand (std = 10.0), long lead time (14 days)
    ss_high = engine.calculate_dynamic_safety_stock(
        daily_demand_mean=20.0,
        daily_demand_std=10.0,
        lead_time_days=14.0,
        lead_time_std=3.0,
        service_level=95.0,
    )
    
    # High volatility must require strictly more safety buffer
    assert ss_high > ss_low
    assert ss_low > 0


def test_inventory_recommender_urgency_classification():
    engine = InventoryRecommendationEngine(default_lead_time_days=7.0)
    
    # Case 1: Critical (only 20 units with 20 daily run rate -> 1 day coverage)
    rec_crit = engine.evaluate_inventory_position(
        product_id="P1",
        store_id="S1",
        current_inventory=20.0,
        daily_demand_forecast=20.0,
    )
    assert rec_crit.urgency == StockoutUrgency.CRITICAL
    assert rec_crit.action_required is True
    assert rec_crit.recommended_order_quantity > 0
    
    # Case 2: Overstock (2000 units with 10 daily run rate -> 200 days coverage)
    rec_over = engine.evaluate_inventory_position(
        product_id="P2",
        store_id="S1",
        current_inventory=2000.0,
        daily_demand_forecast=10.0,
    )
    assert rec_over.urgency == StockoutUrgency.OVERSTOCK
    assert rec_over.action_required is False
    assert rec_over.recommended_order_quantity == 0.0


def test_anomaly_detector():
    detector = SupplyChainAnomalyDetector(z_threshold=2.5)
    
    records = []
    base_date = datetime(2026, 1, 1)
    for d in range(25):
        curr_date = base_date + timedelta(days=d)
        # Normal demand around 10, with a massive spike on day 20
        val = 100.0 if d == 20 else (10.0 + (d % 2))
        records.append({
            "product_id": "P1",
            "store_id": "S1",
            "demand_date": curr_date.strftime("%Y-%m-%d"),
            "daily_demand": val,
        })
    df = pd.DataFrame(records)
    anomalies = detector.detect_demand_anomalies(df)
    
    assert len(anomalies) > 0
    assert (anomalies["anomaly_type"] == "DEMAND_SURGE").any()
