"""
Model Registry & Lifecycle Management.
Governs model versioning, state transitions, Champion identification, and rollback mechanisms.
"""

import os
import json
from enum import Enum
from datetime import datetime
from typing import Dict, Any, Optional, List


class ModelStage(str, Enum):
    CANDIDATE = "CANDIDATE"
    VALIDATION = "VALIDATION"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"
    ARCHIVED = "ARCHIVED"


class ModelRegistry:
    """
    Central registry for tracking model versions, metadata, and lifecycle stages.
    """

    def __init__(self, registry_file: str = "reports/model_registry.json"):
        self.registry_file = registry_file
        self.catalog: Dict[str, Any] = self._load_catalog()

    def _load_catalog(self) -> Dict[str, Any]:
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"models": {}, "last_updated": datetime.now().isoformat()}

    def _save_catalog(self):
        os.makedirs(os.path.dirname(self.registry_file) or ".", exist_ok=True)
        self.catalog["last_updated"] = datetime.now().isoformat()
        with open(self.registry_file, "w") as f:
            json.dump(self.catalog, f, indent=2)

    def register_model(
        self,
        model_name: str,
        run_id: str,
        model_type: str,
        artifact_path: str,
        metrics: Dict[str, float],
        parameters: Optional[Dict[str, Any]] = None,
        feature_names: Optional[List[str]] = None,
        stage: ModelStage = ModelStage.CANDIDATE,
    ) -> int:
        """
        Registers a new model version in the registry.
        """
        if model_name not in self.catalog["models"]:
            self.catalog["models"][model_name] = {"versions": []}

        existing_versions = self.catalog["models"][model_name]["versions"]
        new_version_num = len(existing_versions) + 1

        version_record = {
            "version": new_version_num,
            "run_id": run_id,
            "model_type": model_type,
            "artifact_path": artifact_path,
            "metrics": metrics,
            "parameters": parameters or {},
            "feature_names": feature_names or [],
            "stage": stage.value,
            "registered_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        existing_versions.append(version_record)
        self._save_catalog()
        return new_version_num

    def transition_stage(
        self,
        model_name: str,
        version: int,
        target_stage: ModelStage,
        archive_existing_prod: bool = True,
    ) -> bool:
        """
        Transitions a model version to a new lifecycle stage.
        If moving to PRODUCTION, existing PRODUCTION model is transitioned to ARCHIVED.
        """
        if model_name not in self.catalog["models"]:
            raise ValueError(f"Model '{model_name}' not found in registry.")

        versions = self.catalog["models"][model_name]["versions"]
        target_ver_idx = None

        for idx, v in enumerate(versions):
            if v["version"] == version:
                target_ver_idx = idx
                break

        if target_ver_idx is None:
            raise ValueError(f"Version {version} for model '{model_name}' not found.")

        # If transitioning to PRODUCTION, archive any current PRODUCTION champion
        if target_stage == ModelStage.PRODUCTION and archive_existing_prod:
            for v in versions:
                if v["stage"] == ModelStage.PRODUCTION.value and v["version"] != version:
                    v["stage"] = ModelStage.ARCHIVED.value
                    v["updated_at"] = datetime.now().isoformat()

        versions[target_ver_idx]["stage"] = target_stage.value
        versions[target_ver_idx]["updated_at"] = datetime.now().isoformat()
        self._save_catalog()
        return True

    def get_production_model(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Returns metadata for the currently active PRODUCTION model (Champion).
        """
        if model_name not in self.catalog["models"]:
            return None

        for v in reversed(self.catalog["models"][model_name]["versions"]):
            if v["stage"] == ModelStage.PRODUCTION.value:
                return v
        return None

    def get_all_versions(self, model_name: str) -> List[Dict[str, Any]]:
        """Returns all registered versions for a given model."""
        if model_name not in self.catalog["models"]:
            return []
        return self.catalog["models"][model_name]["versions"]
