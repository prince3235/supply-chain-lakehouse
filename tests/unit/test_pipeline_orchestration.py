"""
Unit Tests for Daily Forecast & Replenishment Pipeline Orchestration.
"""

import os
import pytest
import pandas as pd
from datetime import datetime, timedelta

from pipelines.daily_forecast_pipeline import DailyForecastPipeline


@pytest.fixture
def sample_pipeline_data():
    base_date = datetime(2026, 1, 1)
    demand_records = []
    inv_records = []

    for p in ["P101", "P102"]:
        for s in ["S01"]:
            for d in range(40):
                curr = base_date + timedelta(days=d)
                demand_records.append({
                    "product_id": p,
                    "store_id": s,
                    "demand_date": curr.strftime("%Y-%m-%d"),
                    "daily_demand": 15.0 + (d % 4) * 2.0,
                    "unit_price": 20.0,
                    "total_available": 60.0,
                    "current_safety_stock": 15.0,
                })

            inv_records.append({
                "product_id": p,
                "store_id": s,
                "total_available": 30.0,
                "total_reserved": 5.0,
                "in_transit": 10.0,
                "lead_time_days": 5.0,
            })

    return pd.DataFrame(demand_records), pd.DataFrame(inv_records)


def test_daily_forecast_pipeline_execution(sample_pipeline_data, tmp_path):
    demand_df, inv_df = sample_pipeline_data
    output_dir = str(tmp_path / "pipeline_runs")

    pipeline = DailyForecastPipeline(output_dir=output_dir, horizon_days=7)
    results = pipeline.run(historical_demand_df=demand_df, current_inventory_df=inv_df)

    assert results["summary"]["status"] == "SUCCESS"
    assert results["summary"]["forecast_records_generated"] == 7 * 2  # 7 days * 2 products
    assert results["summary"]["replenishment_evaluations"] == 2
    assert os.path.exists(results["manifest_path"])

    assert len(results["forecast_df"]) == 14
    assert len(results["recommendations_df"]) == 2
