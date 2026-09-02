"""
Statistical Data Drift & Distribution Shift Detector.
Implements Population Stability Index (PSI) and distribution checks for ML monitoring.
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Union
import numpy as np
import pandas as pd


class DriftStatus(str, Enum):
    NO_DRIFT = "NO_DRIFT"          # PSI < 0.10: Distributions are stable
    MODERATE = "MODERATE"          # 0.10 <= PSI < 0.25: Slight shift, monitor closely
    SIGNIFICANT = "SIGNIFICANT"    # PSI >= 0.25: Significant distribution change, retraining recommended


def calculate_psi(
    expected: Union[np.ndarray, pd.Series],
    actual: Union[np.ndarray, pd.Series],
    num_bins: int = 10,
    epsilon: float = 1e-4,
) -> float:
    """
    Calculates the Population Stability Index (PSI) between baseline (expected) and target (actual) arrays.
    
    Formula:
        PSI = sum( (Actual% - Expected%) * ln(Actual% / Expected%) )
    """
    exp_arr = np.asarray(expected, dtype=float)
    act_arr = np.asarray(actual, dtype=float)

    # Drop NaNs
    exp_arr = exp_arr[~np.isnan(exp_arr)]
    act_arr = act_arr[~np.isnan(act_arr)]

    if len(exp_arr) == 0 or len(act_arr) == 0:
        return 0.0

    # Determine quantile bins based on expected baseline
    quantiles = np.linspace(0, 100, num_bins + 1)
    bins = np.percentile(exp_arr, quantiles)
    bins = np.unique(bins)

    if len(bins) < 2:
        return 0.0

    # Adjust boundary edges
    bins[0] = -np.inf
    bins[-1] = np.inf

    # Calculate frequency counts
    exp_counts, _ = np.histogram(exp_arr, bins=bins)
    act_counts, _ = np.histogram(act_arr, bins=bins)

    # Convert to proportions
    exp_pct = exp_counts / float(len(exp_arr))
    act_pct = act_counts / float(len(act_arr))

    # Apply epsilon smoothing to prevent log(0) or division by 0
    exp_pct = np.where(exp_pct == 0, epsilon, exp_pct)
    act_pct = np.where(act_pct == 0, epsilon, act_pct)

    # Calculate PSI per bin
    psi_value = np.sum((act_pct - exp_pct) * np.log(act_pct / exp_pct))
    return float(round(max(0.0, psi_value), 4))


class DriftDetector:
    """
    Monitors feature and prediction drift across batches or time periods.
    """

    def __init__(
        self,
        moderate_threshold: float = 0.10,
        significant_threshold: float = 0.25,
    ):
        self.moderate_threshold = moderate_threshold
        self.significant_threshold = significant_threshold

    def classify_psi(self, psi: float) -> DriftStatus:
        """Classifies PSI score into severity levels."""
        if psi < self.moderate_threshold:
            return DriftStatus.NO_DRIFT
        elif psi < self.significant_threshold:
            return DriftStatus.MODERATE
        else:
            return DriftStatus.SIGNIFICANT

    def detect_dataset_drift(
        self,
        baseline_df: pd.DataFrame,
        target_df: pd.DataFrame,
        features_to_check: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Calculates drift metrics for each numeric feature between baseline and target.
        
        Args:
            baseline_df: Reference/training feature dataset.
            target_df: Current/inference feature dataset.
            features_to_check: Subset of columns to monitor. If None, uses all common numeric columns.
            
        Returns:
            Dictionary containing individual feature PSI, summary counts, and overall status.
        """
        if features_to_check is None:
            common_cols = [c for c in baseline_df.columns if c in target_df.columns]
            features_to_check = [
                c for c in common_cols
                if pd.api.types.is_numeric_dtype(baseline_df[c]) and pd.api.types.is_numeric_dtype(target_df[c])
            ]

        feature_reports = []
        significant_count = 0
        moderate_count = 0

        for feat in features_to_check:
            psi = calculate_psi(baseline_df[feat], target_df[feat])
            status = self.classify_psi(psi)

            if status == DriftStatus.SIGNIFICANT:
                significant_count += 1
            elif status == DriftStatus.MODERATE:
                moderate_count += 1

            feature_reports.append({
                "feature": feat,
                "psi": psi,
                "status": status.value,
            })

        # Overall dataset health classification
        if significant_count > 0:
            overall_status = DriftStatus.SIGNIFICANT
        elif moderate_count >= max(1, len(features_to_check) // 3):
            overall_status = DriftStatus.MODERATE
        else:
            overall_status = DriftStatus.NO_DRIFT

        return {
            "overall_status": overall_status.value,
            "drift_detected": overall_status != DriftStatus.NO_DRIFT,
            "total_features_evaluated": len(features_to_check),
            "features_with_significant_drift": significant_count,
            "features_with_moderate_drift": moderate_count,
            "feature_details": feature_reports,
        }
