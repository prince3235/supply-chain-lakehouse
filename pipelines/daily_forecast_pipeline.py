"""
Daily Batch Forecast & Replenishment Orchestration Pipeline.
Executes the automated end-to-end workflow: Features -> Inference -> Replenishment -> Drift & Anomalies.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd

from src.features.pipeline import FeaturePipeline
from src.training.models import DemandForecaster
from src.inference.batch_predict import BatchInferenceEngine
from src.inference.inventory_recommender import InventoryRecommendationEngine
from src.inference.anomaly_detector import SupplyChainAnomalyDetector
from src.monitoring.drift_detector import DriftDetector


class DailyForecastPipeline:
    """
    Automated daily batch runner orchestrating downstream ML and decision workflows.
    """

    def __init__(
        self,
        output_dir: str = "reports/pipeline_runs",
        horizon_days: int = 14,
    ):
        self.output_dir = output_dir
        self.horizon_days = horizon_days
        os.makedirs(self.output_dir, exist_ok=True)

        self.feature_pipeline = FeaturePipeline()
        self.recommender = InventoryRecommendationEngine()
        self.anomaly_detector = SupplyChainAnomalyDetector()
        self.drift_detector = DriftDetector()

    def run(
        self,
        historical_demand_df: pd.DataFrame,
        current_inventory_df: pd.DataFrame,
        model_obj: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Executes complete daily batch processing run.
        """
        start_time = datetime.now()
        run_id = f"batch_{start_time.strftime('%Y%m%d_%H%M%S')}"

        # 1. Feature Engineering
        feature_df = self.feature_pipeline.build_features(historical_demand_df, fill_na=True)
        X, y, feature_names = self.feature_pipeline.get_feature_matrix(feature_df)

        # 2. Model Initialization (if none provided, fit fresh gradient boosting candidate)
        if model_obj is None:
            model = DemandForecaster(model_type="gradient_boosting", feature_names=feature_names)
            model.fit(X, y)
        else:
            model = model_obj

        # 3. Batch Forecast Inference
        inference_engine = BatchInferenceEngine(
            model_obj=model,
            feature_pipeline=self.feature_pipeline,
        )
        forecast_df = inference_engine.generate_forecasts(
            historical_df=historical_demand_df,
            horizon_days=self.horizon_days,
        )

        # 4. Inventory Replenishment Recommendations
        recommendations_df = self.recommender.generate_recommendations(
            forecast_df=forecast_df,
            inventory_df=current_inventory_df,
        )

        # 5. Anomaly Detection
        demand_anomalies = self.anomaly_detector.detect_demand_anomalies(
            df=historical_demand_df,
            entity_cols=["product_id", "store_id"],
        )

        # 6. Drift Monitoring (compare first half vs second half of historical data)
        mid_point = len(feature_df) // 2
        df_base = feature_df.iloc[:mid_point]
        df_curr = feature_df.iloc[mid_point:]
        drift_report = self.drift_detector.detect_dataset_drift(df_base, df_curr)

        # 7. Summary & Persistence
        end_time = datetime.now()
        critical_stockouts = int((recommendations_df["urgency"] == "CRITICAL").sum())
        actionable_orders = int(recommendations_df["action_required"].sum())

        run_summary = {
            "run_id": run_id,
            "status": "SUCCESS",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": round((end_time - start_time).total_seconds(), 2),
            "forecast_records_generated": len(forecast_df),
            "replenishment_evaluations": len(recommendations_df),
            "actionable_orders_count": actionable_orders,
            "critical_stockout_alerts": critical_stockouts,
            "anomalies_detected_count": len(demand_anomalies),
            "drift_status": drift_report["overall_status"],
            "drift_detected": drift_report["drift_detected"],
        }

        # Persist report
        manifest_path = os.path.join(self.output_dir, f"{run_id}_summary.json")
        with open(manifest_path, "w") as f:
            json.dump(run_summary, f, indent=2)

        return {
            "summary": run_summary,
            "forecast_df": forecast_df,
            "recommendations_df": recommendations_df,
            "anomalies_df": demand_anomalies,
            "drift_report": drift_report,
            "manifest_path": manifest_path,
        }
