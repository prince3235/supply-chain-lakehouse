import pytest
import pandas as pd
from datetime import datetime
from src.inventory import build_inventory_health


def test_build_inventory_health(spark_session):
    data = {
        "inventory_id":       ["INV1", "INV2", "INV3"],
        "product_id":         ["P1",   "P1",   "P2"],
        "store_id":           ["S1",   "S1",   "S2"],
        "warehouse_id":       ["W1",   "W1",   None],
        "snapshot_timestamp": [datetime(2026, 8, 1, 10, 0),
                               datetime(2026, 8, 1, 14, 0),
                               datetime(2026, 8, 1, 10, 0)],
        "available_quantity": [50,   20,  200],
        "reserved_quantity":  [10,    5,   10],
        "reorder_point":      [20,   10,   50],
        "safety_stock":       [100,  50,  100],
        "inventory_value":    [500.0, 200.0, 2000.0],
    }
    df = spark_session.createDataFrame(pd.DataFrame(data))

    result_df = build_inventory_health(df)
    result = result_df.collect()

    assert len(result) == 2

    p1_row = [r for r in result if r["product_id"] == "P1"][0]
    assert p1_row["total_available"] == 70          # 50 + 20
    assert p1_row["total_reserved"] == 15            # 10 + 5
    assert p1_row["current_safety_stock"] == 150     # 100 + 50
    assert p1_row["total_inventory_value"] == 700.0
    assert p1_row["stockout_risk_indicator"] is True  # 70 < 150

    p2_row = [r for r in result if r["product_id"] == "P2"][0]
    assert p2_row["total_available"] == 200
    assert p2_row["stockout_risk_indicator"] is False  # 200 > 100
