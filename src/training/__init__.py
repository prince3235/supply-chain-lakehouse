"""
Supply Chain Lakehouse — Machine Learning Training & Evaluation Module.
Provides model architectures, baselines, temporal validation, and supply-chain metrics.
"""

from src.training.metrics import (
    calculate_mae,
    calculate_rmse,
    calculate_wape,
    calculate_mape,
    calculate_forecast_bias,
    evaluate_forecast_predictions,
)
from src.training.baseline import (
    NaivePreviousDayBaseline,
    MovingAverageBaseline,
)
from src.training.models import DemandForecaster
from src.training.validation import (
    TemporalTimeSeriesSplit,
    cross_validate_temporal,
)
from src.training.train import train_and_evaluate_models
from src.training.tracking import ExperimentTracker
from src.training.registry import ModelRegistry, ModelStage
from src.training.evaluator import ChampionChallengerEvaluator, PromotionDecision

__all__ = [
    "calculate_mae",
    "calculate_rmse",
    "calculate_wape",
    "calculate_mape",
    "calculate_forecast_bias",
    "evaluate_forecast_predictions",
    "NaivePreviousDayBaseline",
    "MovingAverageBaseline",
    "DemandForecaster",
    "TemporalTimeSeriesSplit",
    "cross_validate_temporal",
    "train_and_evaluate_models",
    "ExperimentTracker",
    "ModelRegistry",
    "ModelStage",
    "ChampionChallengerEvaluator",
    "PromotionDecision",
]

