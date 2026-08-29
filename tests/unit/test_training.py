"""
Unit Tests for Machine Learning Demand Forecasting.
Tests metrics, baselines, model regressors, temporal splitting, and leaderboard generation.
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from src.training.metrics import (
    calculate_mae,
    calculate_rmse,
    calculate_wape,
    calculate_forecast_bias,
    calculate_tracking_signal,
    evaluate_forecast_predictions,
)
from src.training.baseline import NaivePreviousDayBaseline, MovingAverageBaseline
from src.training.models import DemandForecaster
from src.training.validation import TemporalTimeSeriesSplit, cross_validate_temporal
from src.training.train import train_and_evaluate_models
from src.features.pipeline import FeaturePipeline


@pytest.fixture
def sample_feature_matrix():
    """Generates 60 days of synthetic feature data for 2 entities."""
    records = []
    base_date = datetime(2026, 1, 1)
    
    for entity in [("P1", "S1"), ("P2", "S1")]:
        p, s = entity
        for d in range(60):
            curr_date = base_date + timedelta(days=d)
            # Upward trending demand with weekly seasonality
            demand = 20.0 + 0.5 * d + 5.0 * np.sin(2 * np.pi * d / 7.0)
            records.append({
                "product_id": p,
                "store_id": s,
                "demand_date": curr_date.strftime("%Y-%m-%d"),
                "daily_demand": demand,
                "unit_price": 30.0,
                "total_available": 150.0,
                "current_safety_stock": 25.0,
            })
            
    df = pd.DataFrame(records)
    pipeline = FeaturePipeline()
    return pipeline.build_features(df)


def test_forecasting_metrics():
    y_true = np.array([10.0, 20.0, 30.0, 40.0])
    y_pred = np.array([12.0, 18.0, 33.0, 35.0])
    
    # Absolute errors: [2, 2, 3, 5] -> sum = 12
    mae = calculate_mae(y_true, y_pred)
    assert mae == 3.0  # 12 / 4 = 3
    
    # Total actual = 100 -> WAPE = 12 / 100 * 100 = 12.0%
    wape = calculate_wape(y_true, y_pred)
    assert wape == 12.0
    
    # Net error (pred - true) = [2, -2, 3, -5] = -2 -> Bias = -2 / 100 = -2.0%
    bias = calculate_forecast_bias(y_true, y_pred)
    assert bias == -2.0
    
    eval_dict = evaluate_forecast_predictions(y_true, y_pred)
    assert "mae" in eval_dict
    assert "wape" in eval_dict
    assert "rmse" in eval_dict


def test_baseline_models(sample_feature_matrix):
    X = sample_feature_matrix
    y = sample_feature_matrix["daily_demand"]
    
    naive = NaivePreviousDayBaseline().fit(X, y)
    naive_preds = naive.predict(X)
    assert len(naive_preds) == len(X)
    assert (naive_preds >= 0).all()
    
    ma = MovingAverageBaseline().fit(X, y)
    ma_preds = ma.predict(X)
    assert len(ma_preds) == len(X)
    assert (ma_preds >= 0).all()


def test_demand_forecaster_models(sample_feature_matrix):
    pipeline = FeaturePipeline()
    X, y, feature_names = pipeline.get_feature_matrix(sample_feature_matrix)
    
    for model_type in ["random_forest", "gradient_boosting"]:
        forecaster = DemandForecaster(model_type=model_type, feature_names=feature_names)
        forecaster.fit(X, y)
        preds = forecaster.predict(X)
        
        assert len(preds) == len(y)
        assert (preds >= 0).all()
        
        importances = forecaster.get_feature_importances()
        assert len(importances) > 0


def test_temporal_time_series_split(sample_feature_matrix):
    splitter = TemporalTimeSeriesSplit(date_col="demand_date", n_splits=2, test_days=7)
    splits = splitter.split(sample_feature_matrix)
    
    assert len(splits) == 2
    for train_idx, val_idx in splits:
        train_dates = sample_feature_matrix.iloc[train_idx]["demand_date"]
        val_dates = sample_feature_matrix.iloc[val_idx]["demand_date"]
        # Invariant: Max train date MUST be strictly less than min val date
        assert train_dates.max() < val_dates.min()


def test_train_and_evaluate_pipeline(sample_feature_matrix):
    results = train_and_evaluate_models(
        feature_df=sample_feature_matrix,
        date_col="demand_date",
        target_col="daily_demand",
        holdout_days=14,
    )
    
    leaderboard = results["leaderboard"]
    assert len(leaderboard) >= 4
    assert "baseline_naive" in leaderboard["model_name"].values
    assert "baseline_moving_avg" in leaderboard["model_name"].values
    assert results["best_model"] is not None
