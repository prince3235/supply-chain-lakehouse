"""
Production Model Performance Monitor & Retraining Trigger.
Tracks rolling forecast error KPIs (WAPE, MAE, Bias) and triggers automated alerts.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

from src.training.metrics import evaluate_forecast_predictions


class ModelHealthStatus(str, Enum):
    HEALTHY = "HEALTHY"            # Error within optimal bounds
    WARNING = "WARNING"            # Error degraded slightly, monitoring needed
    DEGRADED = "DEGRADED"          # Significant error degradation, retraining required


class PerformanceMonitor:
    """
    Evaluates rolling actual vs forecast accuracy to detect model degradation.
    """

    def __init__(
        self,
        wape_warning_threshold: float = 20.0,
        wape_critical_threshold: float = 30.0,
        bias_warning_threshold: float = 10.0,
        bias_critical_threshold: float = 20.0,
    ):
        self.wape_warning = wape_warning_threshold
        self.wape_critical = wape_critical_threshold
        self.bias_warning = bias_warning_threshold
        self.bias_critical = bias_critical_threshold

    def evaluate_live_performance(
        self,
        actuals: np.ndarray,
        predictions: np.ndarray,
        model_name: str = "demand_forecaster",
        model_version: int = 1,
    ) -> Dict[str, Any]:
        """
        Calculates live performance metrics and determines model health status.
        """
        metrics = evaluate_forecast_predictions(actuals, predictions)
        wape = metrics["wape"]
        bias = abs(metrics["forecast_bias_pct"])

        # Determine health state
        if wape >= self.wape_critical or bias >= self.bias_critical:
            status = ModelHealthStatus.DEGRADED
            trigger_retraining = True
            reason = f"Critical degradation: WAPE ({wape}%) or Forecast Bias ({bias}%) exceeded critical limits."
        elif wape >= self.wape_warning or bias >= self.bias_warning:
            status = ModelHealthStatus.WARNING
            trigger_retraining = False
            reason = f"Warning: WAPE ({wape}%) or Forecast Bias ({bias}%) breached warning threshold."
        else:
            status = ModelHealthStatus.HEALTHY
            trigger_retraining = False
            reason = f"Model is performing within normal bounds (WAPE: {wape}%, Bias: {bias}%)."

        return {
            "model_name": model_name,
            "model_version": model_version,
            "status": status.value,
            "trigger_retraining": trigger_retraining,
            "reason": reason,
            "metrics": metrics,
        }
