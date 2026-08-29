"""
Unified Training & Baseline Comparison Pipeline.
Trains candidate ML models, compares them against statistical baselines, and generates model leaderboards.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

from src.training.baseline import NaivePreviousDayBaseline, MovingAverageBaseline
from src.training.models import DemandForecaster
from src.training.metrics import evaluate_forecast_predictions


def train_and_evaluate_models(
    feature_df: pd.DataFrame,
    date_col: str = "demand_date",
    target_col: str = "daily_demand",
    feature_cols: Optional[List[str]] = None,
    holdout_days: int = 14,
) -> Dict[str, Any]:
    """
    Executes benchmark comparison across Baselines and ML architectures.
    
    Args:
        feature_df: Enriched feature DataFrame.
        date_col: Timestamp column.
        target_col: Demand target column.
        feature_cols: List of features to supply to ML models.
        holdout_days: Number of most recent days reserved for final holdout testing.
        
    Returns:
        Dictionary containing leaderboard, metrics, and trained model objects.
    """
    df = feature_df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df[date_col] = pd.to_datetime(df[date_col])

    # Split into Historical Training and Future Holdout
    unique_dates = np.sort(df[date_col].unique())
    if len(unique_dates) <= holdout_days:
        split_date = unique_dates[len(unique_dates) // 2]
    else:
        split_date = unique_dates[-holdout_days]

    train_mask = df[date_col] < split_date
    test_mask = df[date_col] >= split_date

    train_df = df[train_mask].reset_index(drop=True)
    test_df = df[test_mask].reset_index(drop=True)

    if feature_cols is None:
        exclude_cols = {date_col, target_col, "product_id", "store_id", "category"}
        feature_cols = [c for c in df.columns if c not in exclude_cols and pd.api.types.is_numeric_dtype(df[c])]

    X_train, y_train = train_df[feature_cols], train_df[target_col]
    X_test, y_test = test_df[feature_cols], test_df[target_col]

    models_to_evaluate = {
        "baseline_naive": NaivePreviousDayBaseline(),
        "baseline_moving_avg": MovingAverageBaseline(),
        "model_random_forest": DemandForecaster(model_type="random_forest", feature_names=feature_cols),
        "model_gradient_boosting": DemandForecaster(model_type="gradient_boosting", feature_names=feature_cols),
    }

    results = {}
    leaderboard_records = []

    # Train and evaluate all candidates
    for name, model in models_to_evaluate.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        metrics = evaluate_forecast_predictions(y_test, preds)

        results[name] = {
            "model": model,
            "metrics": metrics,
            "predictions": preds,
        }

        leaderboard_records.append({
            "model_name": name,
            "is_baseline": name.startswith("baseline"),
            "mae": metrics["mae"],
            "rmse": metrics["rmse"],
            "wape": metrics["wape"],
            "mape": metrics["mape"],
            "bias_pct": metrics["forecast_bias_pct"],
        })

    leaderboard_df = pd.DataFrame(leaderboard_records).sort_values("wape").reset_index(drop=True)

    # Compute baseline improvement for top ML model
    baseline_wape = results["baseline_moving_avg"]["metrics"]["wape"]
    best_ml_row = leaderboard_df[~leaderboard_df["is_baseline"]].iloc[0]
    best_ml_name = best_ml_row["model_name"]
    best_ml_wape = best_ml_row["wape"]

    improvement_pct = round(((baseline_wape - best_ml_wape) / (baseline_wape + 1e-5)) * 100.0, 2)

    return {
        "leaderboard": leaderboard_df,
        "best_model_name": best_ml_name,
        "best_model": results[best_ml_name]["model"],
        "baseline_wape": baseline_wape,
        "best_ml_wape": best_ml_wape,
        "improvement_pct": improvement_pct,
        "feature_cols": feature_cols,
        "models": results,
    }
