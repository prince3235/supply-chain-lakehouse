"""
Temporal Validation & Cross-Validation Framework.
Enforces strict chronological splitting for time-series forecasting without data leakage.
"""

from typing import List, Tuple, Dict, Any, Optional
import pandas as pd
import numpy as np

from src.training.metrics import evaluate_forecast_predictions


class TemporalTimeSeriesSplit:
    """
    Chronological expanding/rolling window time-series splitter.
    """

    def __init__(
        self,
        date_col: str = "demand_date",
        n_splits: int = 3,
        test_days: int = 14,
        gap_days: int = 0,
    ):
        self.date_col = date_col
        self.n_splits = n_splits
        self.test_days = test_days
        self.gap_days = gap_days

    def split(self, df: pd.DataFrame) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Generates train/validation index pairs respecting chronological ordering.
        
        Args:
            df: DataFrame containing the date_col.
            
        Returns:
            List of (train_indices, val_indices) tuples.
        """
        df = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df[self.date_col]):
            df[self.date_col] = pd.to_datetime(df[self.date_col])

        unique_dates = np.sort(df[self.date_col].unique())
        total_unique_dates = len(unique_dates)

        min_required_dates = self.n_splits * self.test_days + 14
        if total_unique_dates < min_required_dates:
            # Fallback for short sample series
            test_size = max(1, total_unique_dates // (self.n_splits + 1))
            self.test_days = test_size

        splits = []
        for i in range(self.n_splits, 0, -1):
            test_end_idx = total_unique_dates - (i - 1) * self.test_days
            test_start_idx = test_end_idx - self.test_days
            train_end_idx = test_start_idx - self.gap_days

            if train_end_idx <= 0:
                continue

            train_dates = unique_dates[:train_end_idx]
            val_dates = unique_dates[test_start_idx:test_end_idx]

            train_mask = df[self.date_col].isin(train_dates)
            val_mask = df[self.date_col].isin(val_dates)

            train_indices = np.where(train_mask)[0]
            val_indices = np.where(val_mask)[0]

            if len(train_indices) > 0 and len(val_indices) > 0:
                splits.append((train_indices, val_indices))

        return splits


def cross_validate_temporal(
    model,
    X: pd.DataFrame,
    y: pd.Series,
    df_with_dates: pd.DataFrame,
    date_col: str = "demand_date",
    n_splits: int = 3,
    test_days: int = 14,
) -> Dict[str, Any]:
    """
    Executes chronological cross-validation and averages evaluation metrics across folds.
    """
    splitter = TemporalTimeSeriesSplit(
        date_col=date_col,
        n_splits=n_splits,
        test_days=test_days,
    )
    splits = splitter.split(df_with_dates)

    fold_metrics = []
    for fold_num, (train_idx, val_idx) in enumerate(splits, start=1):
        X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
        X_val, y_val = X.iloc[val_idx], y.iloc[val_idx]

        model.fit(X_train, y_train)
        preds = model.predict(X_val)
        metrics = evaluate_forecast_predictions(y_val, preds)
        metrics["fold"] = fold_num
        fold_metrics.append(metrics)

    # Compute summary averages
    df_metrics = pd.DataFrame(fold_metrics)
    summary = {
        "mean_mae": round(float(df_metrics["mae"].mean()), 4),
        "mean_rmse": round(float(df_metrics["rmse"].mean()), 4),
        "mean_wape": round(float(df_metrics["wape"].mean()), 2),
        "mean_bias": round(float(df_metrics["forecast_bias_pct"].mean()), 2),
        "folds": fold_metrics,
    }
    return summary
