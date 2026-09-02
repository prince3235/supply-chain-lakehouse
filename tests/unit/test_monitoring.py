"""
Unit Tests for Monitoring & Drift Detection.
"""

import pytest
import numpy as np
import pandas as pd

from src.monitoring.drift_detector import calculate_psi, DriftDetector, DriftStatus
from src.monitoring.performance_monitor import PerformanceMonitor, ModelHealthStatus


def test_calculate_psi_identical_distribution():
    np.random.seed(42)
    baseline = np.random.normal(50, 10, 1000)
    target = np.random.normal(50, 10, 1000)

    psi = calculate_psi(baseline, target)
    assert psi < 0.10, f"Expected low PSI for identical distributions, got {psi}"


def test_calculate_psi_shifted_distribution():
    np.random.seed(42)
    baseline = np.random.normal(50, 10, 1000)
    # Substantial shift in mean and variance
    target = np.random.normal(85, 25, 1000)

    psi = calculate_psi(baseline, target)
    assert psi >= 0.25, f"Expected high PSI for shifted distributions, got {psi}"


def test_drift_detector_dataset():
    np.random.seed(42)
    df_base = pd.DataFrame({
        "lag_1": np.random.normal(20, 5, 500),
        "rolling_mean_7": np.random.normal(20, 4, 500),
        "unit_price": np.random.uniform(10, 50, 500),
    })

    # Target has shifted lag_1
    df_target = pd.DataFrame({
        "lag_1": np.random.normal(60, 15, 500),
        "rolling_mean_7": np.random.normal(20, 4, 500),
        "unit_price": np.random.uniform(10, 50, 500),
    })

    detector = DriftDetector()
    report = detector.detect_dataset_drift(df_base, df_target)

    assert report["drift_detected"] is True
    assert report["features_with_significant_drift"] >= 1
    assert report["total_features_evaluated"] == 3


def test_performance_monitor_states():
    monitor = PerformanceMonitor(
        wape_warning_threshold=20.0,
        wape_critical_threshold=30.0,
    )

    actuals = np.array([100.0, 150.0, 200.0, 250.0])

    # Healthy predictions (5% error)
    preds_healthy = np.array([105.0, 145.0, 205.0, 245.0])
    res_healthy = monitor.evaluate_live_performance(actuals, preds_healthy)
    assert res_healthy["status"] == ModelHealthStatus.HEALTHY.value
    assert res_healthy["trigger_retraining"] is False

    # Degraded predictions (40% error)
    preds_degraded = np.array([60.0, 90.0, 120.0, 150.0])
    res_degraded = monitor.evaluate_live_performance(actuals, preds_degraded)
    assert res_degraded["status"] == ModelHealthStatus.DEGRADED.value
    assert res_degraded["trigger_retraining"] is True
