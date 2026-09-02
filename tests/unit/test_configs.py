"""
Unit Tests for Configuration Files.
Verifies syntax, presence of required sections, and schema consistency.
"""

import os
import yaml
import pytest


def test_forecasting_yaml_schema():
    config_path = os.path.join("configs", "forecasting.yaml")
    assert os.path.exists(config_path), "configs/forecasting.yaml does not exist"

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    assert config["version"] == "1.0.0"
    assert config["target"]["name"] == "daily_demand"
    assert 14 in config["horizons"]["supported"]
    assert "lags" in config["features"]
    assert "candidates" in config["models"]
    assert "champion_challenger" in config["governance"]


def test_monitoring_yaml_schema():
    config_path = os.path.join("configs", "monitoring.yaml")
    assert os.path.exists(config_path), "configs/monitoring.yaml does not exist"

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    assert config["version"] == "1.0.0"
    assert "thresholds" in config["drift_detection"]
    assert "kpi_thresholds" in config["performance_monitoring"]
    assert config["performance_monitoring"]["kpi_thresholds"]["wape"]["warning_pct"] == 20.0
    assert config["retraining_triggers"]["auto_trigger_enabled"] is True
