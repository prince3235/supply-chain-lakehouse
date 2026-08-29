"""
Batch Demand Forecast Inference Engine.
Loads registered production models and generates multi-horizon demand forecasts with confidence intervals.
"""

import os
import pickle
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
import pandas as pd

from src.training.registry import ModelRegistry
from src.features.pipeline import FeaturePipeline


class BatchInferenceEngine:
    """
    Executes batch inference pipelines across product and store hierarchies.
    """

    def __init__(
        self,
        registry: Optional[ModelRegistry] = None,
        model_obj: Optional[Any] = None,
        feature_pipeline: Optional[FeaturePipeline] = None,
    ):
        self.registry = registry or ModelRegistry()
        self.model_obj = model_obj
        self.feature_pipeline = feature_pipeline or FeaturePipeline()
        self.model_version: Optional[int] = None
        self.model_type: Optional[str] = None

    def load_production_model(self, model_name: str = "demand_forecast_model") -> bool:
        """
        Loads the active Champion model from the registry.
        """
        prod_meta = self.registry.get_production_model(model_name)
        if not prod_meta:
            raise RuntimeError(f"No active PRODUCTION model found in registry for '{model_name}'.")

        artifact_path = prod_meta["artifact_path"]
        if not os.path.exists(artifact_path):
            raise FileNotFoundError(f"Model artifact not found at '{artifact_path}'.")

        with open(artifact_path, "rb") as f:
            self.model_obj = pickle.load(f)

        self.model_version = prod_meta["version"]
        self.model_type = prod_meta["model_type"]
        return True

    def generate_forecasts(
        self,
        historical_df: pd.DataFrame,
        horizon_days: int = 14,
        confidence_level: float = 0.95,
    ) -> pd.DataFrame:
        """
        Generates multi-day forward demand predictions for all entity pairs.
        
        Args:
            historical_df: Recent daily demand history containing required feature columns.
            horizon_days: Number of forward days to forecast (e.g., 7, 14, 30).
            confidence_level: Statistical confidence bound (e.g. 0.95 for ~1.96 z-score).
            
        Returns:
            Forecast DataFrame with columns:
            [product_id, store_id, forecast_date, horizon_step, predicted_demand, confidence_lower, confidence_upper, model_version, generated_at]
        """
        if self.model_obj is None:
            raise RuntimeError("Model must be loaded before running inference. Call load_production_model() or pass model_obj.")

        df_features = self.feature_pipeline.build_features(historical_df, fill_na=True)
        date_col = self.feature_pipeline.date_col

        if not pd.api.types.is_datetime64_any_dtype(df_features[date_col]):
            df_features[date_col] = pd.to_datetime(df_features[date_col])

        # Get latest available date per entity
        max_date = df_features[date_col].max()
        latest_records = df_features[df_features[date_col] == max_date].copy()

        z_score = 1.96 if confidence_level >= 0.95 else 1.645
        forecast_records = []
        generated_at = datetime.now().isoformat()

        # Generate rolling multi-step forecasts
        for step in range(1, horizon_days + 1):
            target_forecast_date = max_date + timedelta(days=step)
            current_step_df = latest_records.copy()
            current_step_df[date_col] = target_forecast_date
            
            # Update temporal features for the forward date
            current_step_df = self.feature_pipeline.temporal_builder.transform(current_step_df)
            X, _, _ = self.feature_pipeline.get_feature_matrix(current_step_df)

            # Generate point prediction
            predictions = self.model_obj.predict(X)

            # Estimate standard error of forecast (proportional to horizon step)
            base_uncertainty = np.std(predictions) if len(predictions) > 1 else 2.0
            horizon_uncertainty = max(1.0, base_uncertainty * np.sqrt(step / 7.0))

            for idx, (_, row) in enumerate(latest_records.iterrows()):
                pred_val = max(0.0, float(predictions[idx]))
                lower_bound = max(0.0, pred_val - z_score * horizon_uncertainty)
                upper_bound = pred_val + z_score * horizon_uncertainty

                forecast_records.append({
                    "product_id": row["product_id"],
                    "store_id": row["store_id"],
                    "forecast_date": target_forecast_date.strftime("%Y-%m-%d"),
                    "horizon_step": step,
                    "predicted_demand": round(pred_val, 2),
                    "confidence_lower": round(lower_bound, 2),
                    "confidence_upper": round(upper_bound, 2),
                    "model_version": self.model_version or 1,
                    "model_type": self.model_type or "gradient_boosting",
                    "generated_at": generated_at,
                })

        return pd.DataFrame(forecast_records)
