"""
# Supply Chain Lakehouse — Demand Forecasting & Replenishment Walkthrough
Demonstrates end-to-end ML lifecycle from Gold-layer tables to prescriptive purchase orders.

Can be run directly via:
    python notebooks/01_demand_forecasting_walkthrough.py
"""

from datetime import datetime, timedelta
import numpy as np
import pandas as pd

from src.features.pipeline import FeaturePipeline
from src.training.train import train_and_evaluate_models
from src.inference.batch_predict import BatchInferenceEngine
from src.inference.inventory_recommender import InventoryRecommendationEngine
from src.monitoring.drift_detector import DriftDetector


def run_walkthrough():
    print("=" * 70)
    print("  SUPPLY CHAIN LAKEHOUSE: DEMAND FORECASTING & REPLENISHMENT WALKTHROUGH")
    print("=" * 70)

    # 1. Generate Sample Gold-Layer Historical Demand
    print("\n[Step 1] Generating Historical Gold Demand & Inventory Records...")
    records = []
    base_date = datetime(2026, 1, 1)

    for p_id in ["PROD_LAPTOP_01", "PROD_HEADSET_02"]:
        for s_id in ["STORE_SEATTLE"]:
            for d in range(60):
                curr = base_date + timedelta(days=d)
                # Upward trend + weekly seasonality + noise
                demand = max(2.0, 15.0 + 0.3 * d + 4.0 * np.sin(2 * np.pi * d / 7.0) + np.random.normal(0, 1.5))
                records.append({
                    "product_id": p_id,
                    "store_id": s_id,
                    "demand_date": curr.strftime("%Y-%m-%d"),
                    "daily_demand": round(demand, 1),
                    "unit_price": 120.0 if "LAPTOP" in p_id else 45.0,
                    "total_available": 150.0 - (d % 15) * 8.0,
                    "current_safety_stock": 25.0,
                })

    df_gold = pd.DataFrame(records)
    print(f"Loaded {len(df_gold)} historical daily records across {df_gold['product_id'].nunique()} products.")

    # 2. Extract Features
    print("\n[Step 2] Executing Feature Engineering Pipeline (Zero-Leakage Invariant)...")
    pipeline = FeaturePipeline()
    feature_df = pipeline.build_features(df_gold, fill_na=True)
    X, y, feature_names = pipeline.get_feature_matrix(feature_df)
    print(f"Extracted {len(feature_names)} engineered features. Sample features:")
    for f in feature_names[:8]:
        print(f"  - {f}")

    # 3. Model Tournament: Baseline vs Machine Learning Candidates
    print("\n[Step 3] Running Model Tournament on Future 14-Day Holdout...")
    eval_results = train_and_evaluate_models(feature_df, feature_cols=feature_names, holdout_days=14)
    print("\n--- MODEL LEADERBOARD ---")
    print(eval_results["leaderboard"].to_string(index=False))
    print(f"\nBest Model: {eval_results['best_model_name']}")
    print(f"Improvement over Baseline: +{eval_results['improvement_pct']}% WAPE reduction")

    # 4. Forward Batch Forecasting
    print("\n[Step 4] Generating 14-Day Forward Forecast with 95% Confidence Intervals...")
    engine = BatchInferenceEngine(model_obj=eval_results["best_model"], feature_pipeline=pipeline)
    forecast_df = engine.generate_forecasts(historical_df=df_gold, horizon_days=14)
    print(forecast_df[["product_id", "forecast_date", "predicted_demand", "confidence_lower", "confidence_upper"]].head(6).to_string(index=False))

    # 5. Inventory Replenishment & Decision Intelligence
    print("\n[Step 5] Calculating Dynamic Safety Stock, Reorder Points & Order Quantities...")
    recommender = InventoryRecommendationEngine(default_lead_time_days=7.0)

    inventory_current = pd.DataFrame([
        {"product_id": "PROD_LAPTOP_01", "store_id": "STORE_SEATTLE", "total_available": 40.0},
        {"product_id": "PROD_HEADSET_02", "store_id": "STORE_SEATTLE", "total_available": 180.0},
    ])

    recs_df = recommender.generate_recommendations(forecast_df=forecast_df, inventory_df=inventory_current)
    print(recs_df[["product_id", "current_inventory", "safety_stock", "reorder_point", "recommended_order_qty", "urgency", "action_required"]].to_string(index=False))

    # 6. Data Drift Check
    print("\n[Step 6] Running Statistical Drift Analysis (PSI)...")
    drift_detector = DriftDetector()
    mid = len(feature_df) // 2
    drift_results = drift_detector.detect_dataset_drift(feature_df.iloc[:mid], feature_df.iloc[mid:])
    print(f"Dataset Drift Status: {drift_results['overall_status']}")
    print(f"Significant Drift Features: {drift_results['features_with_significant_drift']}")

    print("\n" + "=" * 70)
    print("  WALKTHROUGH COMPLETE: ALL STEPS EXECUTED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    run_walkthrough()
