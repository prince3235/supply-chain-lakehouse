"""
Unit Tests for MLOps Tracking, Model Registry, and Champion vs Challenger Gate.
"""

import os
import shutil
import pytest
from src.training.tracking import ExperimentTracker
from src.training.registry import ModelRegistry, ModelStage
from src.training.evaluator import ChampionChallengerEvaluator
from src.training.models import DemandForecaster


@pytest.fixture
def temp_mlops_env(tmp_path):
    tracking_dir = str(tmp_path / "experiments")
    registry_file = str(tmp_path / "registry.json")
    return {"tracking_dir": tracking_dir, "registry_file": registry_file}


def test_experiment_tracker(temp_mlops_env):
    tracker = ExperimentTracker(tracking_dir=temp_mlops_env["tracking_dir"])
    
    run_id = tracker.start_run(run_name="test_rf_run", model_type="random_forest")
    assert run_id.startswith("run_")
    
    tracker.log_params({"n_estimators": 50, "max_depth": 5})
    tracker.log_metrics({"mae": 2.5, "wape": 11.2, "rmse": 3.1})
    tracker.log_dataset_info("gold_daily_demand", 500, ["lag_1", "rolling_mean_7"])
    
    dummy_model = DemandForecaster(model_type="random_forest")
    artifact_path = tracker.log_model(dummy_model)
    assert os.path.exists(artifact_path)
    
    run_summary = tracker.end_run(status="COMPLETED")
    assert run_summary["status"] == "COMPLETED"
    assert run_summary["metrics"]["wape"] == 11.2


def test_model_registry_lifecycle(temp_mlops_env):
    registry = ModelRegistry(registry_file=temp_mlops_env["registry_file"])
    model_name = "demand_forecast_model"
    
    # Register Version 1
    v1 = registry.register_model(
        model_name=model_name,
        run_id="run_001",
        model_type="random_forest",
        artifact_path="/tmp/model_v1.pkl",
        metrics={"wape": 15.0, "mae": 4.0},
    )
    assert v1 == 1
    
    # Register Version 2
    v2 = registry.register_model(
        model_name=model_name,
        run_id="run_002",
        model_type="gradient_boosting",
        artifact_path="/tmp/model_v2.pkl",
        metrics={"wape": 12.0, "mae": 3.2},
    )
    assert v2 == 2
    
    # Transition V1 to PRODUCTION (Champion)
    registry.transition_stage(model_name, v1, ModelStage.PRODUCTION)
    champ = registry.get_production_model(model_name)
    assert champ["version"] == 1
    
    # Transition V2 to PRODUCTION -> V1 should be ARCHIVED
    registry.transition_stage(model_name, v2, ModelStage.PRODUCTION)
    new_champ = registry.get_production_model(model_name)
    assert new_champ["version"] == 2
    
    versions = registry.get_all_versions(model_name)
    assert versions[0]["stage"] == ModelStage.ARCHIVED.value
    assert versions[1]["stage"] == ModelStage.PRODUCTION.value


def test_champion_challenger_evaluator(temp_mlops_env):
    registry = ModelRegistry(registry_file=temp_mlops_env["registry_file"])
    evaluator = ChampionChallengerEvaluator(registry, min_improvement_pct=5.0)
    model_name = "demand_forecast_model"
    
    # Register initial model (WAPE = 20%)
    v1 = registry.register_model(
        model_name=model_name,
        run_id="run_001",
        model_type="baseline",
        artifact_path="/tmp/m1.pkl",
        metrics={"wape": 20.0, "mae": 5.0, "forecast_bias_pct": 2.0},
    )
    
    # Case 1: Initial Launch promotion
    dec1 = evaluator.evaluate_and_promote(model_name, challenger_version=v1)
    assert dec1.promoted is True
    assert dec1.status == "INITIAL_PROMOTION"
    
    # Register weaker Challenger (WAPE = 19.5% -> only 2.5% improvement < 5% threshold)
    v2 = registry.register_model(
        model_name=model_name,
        run_id="run_002",
        model_type="rf",
        artifact_path="/tmp/m2.pkl",
        metrics={"wape": 19.5, "mae": 4.9, "forecast_bias_pct": 1.0},
    )
    dec2 = evaluator.evaluate_and_promote(model_name, challenger_version=v2)
    assert dec2.promoted is False
    assert dec2.status == "REJECTED"
    
    # Register superior Challenger (WAPE = 15.0% -> 25% improvement >= 5% threshold)
    v3 = registry.register_model(
        model_name=model_name,
        run_id="run_003",
        model_type="gbm",
        artifact_path="/tmp/m3.pkl",
        metrics={"wape": 15.0, "mae": 3.8, "forecast_bias_pct": -1.5},
    )
    dec3 = evaluator.evaluate_and_promote(model_name, challenger_version=v3)
    assert dec3.promoted is True
    assert dec3.status == "PROMOTED"
    assert dec3.improvement_pct == 25.0
    
    # Verify current production model is now V3
    champ = registry.get_production_model(model_name)
    assert champ["version"] == 3
