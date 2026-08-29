"""
Supply Chain Demand Forecasting Evaluation Metrics.
Implements industry standard KPIs (MAE, RMSE, WAPE, MAPE, Forecast Bias, Tracking Signal).
"""

from typing import Dict, Union
import numpy as np
import pandas as pd


def calculate_mae(y_true: Union[np.ndarray, pd.Series], y_pred: Union[np.ndarray, pd.Series]) -> float:
    """Mean Absolute Error."""
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_pred, dtype=float)
    return float(np.mean(np.abs(y_t - y_p)))


def calculate_rmse(y_true: Union[np.ndarray, pd.Series], y_pred: Union[np.ndarray, pd.Series]) -> float:
    """Root Mean Squared Error."""
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_pred, dtype=float)
    return float(np.sqrt(np.mean((y_t - y_p) ** 2)))


def calculate_wape(y_true: Union[np.ndarray, pd.Series], y_pred: Union[np.ndarray, pd.Series]) -> float:
    """
    Weighted Absolute Percentage Error (WAPE / MAD-to-Mean ratio).
    Standard metric for supply chain demand planning; handles zero actual sales without infinity division.
    Formula: sum(|y_true - y_pred|) / sum(y_true) * 100%
    """
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_pred, dtype=float)
    total_actual = float(np.sum(y_t))
    if total_actual == 0.0:
        return 0.0 if float(np.sum(y_p)) == 0.0 else 100.0
    return float((np.sum(np.abs(y_t - y_p)) / total_actual) * 100.0)


def calculate_mape(y_true: Union[np.ndarray, pd.Series], y_pred: Union[np.ndarray, pd.Series], epsilon: float = 1e-5) -> float:
    """Mean Absolute Percentage Error with epsilon smoothing for zero-demand days."""
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_pred, dtype=float)
    non_zero_mask = y_t > epsilon
    if not np.any(non_zero_mask):
        return 0.0
    return float(np.mean(np.abs((y_t[non_zero_mask] - y_p[non_zero_mask]) / y_t[non_zero_mask])) * 100.0)


def calculate_forecast_bias(y_true: Union[np.ndarray, pd.Series], y_pred: Union[np.ndarray, pd.Series]) -> float:
    """
    Forecast Bias Percentage.
    Positive value indicates overforecasting (risk of excess inventory).
    Negative value indicates underforecasting (risk of stockouts).
    Formula: sum(y_pred - y_true) / sum(y_true) * 100%
    """
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_pred, dtype=float)
    total_actual = float(np.sum(y_t))
    if total_actual == 0.0:
        return 0.0
    return float((np.sum(y_p - y_t) / total_actual) * 100.0)


def calculate_tracking_signal(y_true: Union[np.ndarray, pd.Series], y_pred: Union[np.ndarray, pd.Series]) -> float:
    """
    Tracking Signal: Cumulative Sum of Forecast Errors / Mean Absolute Deviation (MAD).
    A tracking signal between -4 and +4 generally indicates an in-control forecasting model.
    """
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_pred, dtype=float)
    errors = y_t - y_p
    mad = np.mean(np.abs(errors))
    if mad == 0.0:
        return 0.0
    return float(np.sum(errors) / mad)


def evaluate_forecast_predictions(
    y_true: Union[np.ndarray, pd.Series],
    y_pred: Union[np.ndarray, pd.Series],
) -> Dict[str, float]:
    """
    Evaluates predictions and returns a comprehensive dictionary of all supply chain metrics.
    """
    return {
        "mae": round(calculate_mae(y_true, y_pred), 4),
        "rmse": round(calculate_rmse(y_true, y_pred), 4),
        "wape": round(calculate_wape(y_true, y_pred), 2),
        "mape": round(calculate_mape(y_true, y_pred), 2),
        "forecast_bias_pct": round(calculate_forecast_bias(y_true, y_pred), 2),
        "tracking_signal": round(calculate_tracking_signal(y_true, y_pred), 4),
    }
