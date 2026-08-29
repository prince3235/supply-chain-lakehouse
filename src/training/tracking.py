"""
MLOps Experiment Tracking.
Logs parameters, metrics, dataset lineage, and serializes model artifacts for reproducible ML.
"""

import os
import json
import uuid
import pickle
from datetime import datetime
from typing import Dict, Any, Optional, List


class ExperimentTracker:
    """
    Tracks and persists ML experiment runs, configurations, and evaluation metrics.
    """

    def __init__(self, tracking_dir: str = "reports/ml_experiments"):
        self.tracking_dir = tracking_dir
        os.makedirs(self.tracking_dir, exist_ok=True)
        self.active_run_id: Optional[str] = None
        self.active_run_data: Dict[str, Any] = {}

    def start_run(self, run_name: str, model_type: str, tags: Optional[Dict[str, str]] = None) -> str:
        """
        Initializes a new tracking run.
        """
        self.active_run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        self.active_run_data = {
            "run_id": self.active_run_id,
            "run_name": run_name,
            "model_type": model_type,
            "start_time": datetime.now().isoformat(),
            "status": "RUNNING",
            "tags": tags or {},
            "parameters": {},
            "metrics": {},
            "artifacts": {},
            "dataset_info": {},
        }
        return self.active_run_id

    def log_params(self, params: Dict[str, Any]):
        """Logs model hyperparameters or experiment configurations."""
        if not self.active_run_id:
            raise RuntimeError("No active experiment run found. Call start_run first.")
        self.active_run_data["parameters"].update(params)

    def log_metrics(self, metrics: Dict[str, float]):
        """Logs evaluation metrics (MAE, WAPE, RMSE, etc.)."""
        if not self.active_run_id:
            raise RuntimeError("No active experiment run found. Call start_run first.")
        self.active_run_data["metrics"].update(metrics)

    def log_dataset_info(self, dataset_name: str, num_records: int, feature_names: List[str]):
        """Logs dataset lineage and feature signature."""
        if not self.active_run_id:
            raise RuntimeError("No active experiment run found. Call start_run first.")
        self.active_run_data["dataset_info"] = {
            "dataset_name": dataset_name,
            "num_records": num_records,
            "feature_count": len(feature_names),
            "features": feature_names,
        }

    def log_model(self, model_obj: Any, model_name: str = "model.pkl") -> str:
        """Serializes and saves the trained model artifact."""
        if not self.active_run_id:
            raise RuntimeError("No active experiment run found. Call start_run first.")

        run_artifacts_dir = os.path.join(self.tracking_dir, self.active_run_id)
        os.makedirs(run_artifacts_dir, exist_ok=True)
        model_path = os.path.join(run_artifacts_dir, model_name)

        with open(model_path, "wb") as f:
            pickle.dump(model_obj, f)

        self.active_run_data["artifacts"]["model_path"] = model_path
        return model_path

    def end_run(self, status: str = "COMPLETED") -> Dict[str, Any]:
        """Finalizes run metadata and persists run summary to disk."""
        if not self.active_run_id:
            raise RuntimeError("No active experiment run found.")

        self.active_run_data["status"] = status
        self.active_run_data["end_time"] = datetime.now().isoformat()

        run_artifacts_dir = os.path.join(self.tracking_dir, self.active_run_id)
        os.makedirs(run_artifacts_dir, exist_ok=True)
        manifest_path = os.path.join(run_artifacts_dir, "run_manifest.json")

        with open(manifest_path, "w") as f:
            json.dump(self.active_run_data, f, indent=2)

        completed_data = self.active_run_data.copy()
        self.active_run_id = None
        self.active_run_data = {}
        return completed_data
