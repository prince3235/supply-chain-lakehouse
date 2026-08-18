import pytest
import pandas as pd
from datetime import datetime
from src.suppliers import build_supplier_performance


def test_build_supplier_performance(spark_session):
    data = {
        "shipment_id": ["SHP1", "SHP2", "SHP3"],
        "supplier_id": ["SUP1", "SUP1", "SUP2"],
        "product_id":  ["P1",   "P1",   "P2"],
        "warehouse_id":["W1",   "W1",   "W2"],
        "order_date":  [datetime(2026, 8, 1), datetime(2026, 8, 2), datetime(2026, 8, 1)],
        "expected_delivery_date": [datetime(2026, 8, 5),  datetime(2026, 8, 10), datetime(2026, 8, 20)],
        "actual_delivery_date":   [datetime(2026, 8, 6),  datetime(2026, 8, 10), datetime(2026, 8, 20)],
        "quantity":    [100, 50, 200],
        "status":      ["DELIVERED", "DELIVERED", "DELIVERED"],
        "delay_days":  [1, 0, 0],
    }
    df = spark_session.createDataFrame(pd.DataFrame(data))

    result_df = build_supplier_performance(df)
    result = result_df.collect()

    assert len(result) == 2

    sup1_row = [r for r in result if r["supplier_id"] == "SUP1"][0]
    assert sup1_row["total_shipments"] == 2
    assert sup1_row["delayed_shipments"] == 1
    assert sup1_row["average_delay_days"] == 0.5   # (1 + 0) / 2
    assert sup1_row["on_time_rate"] == 0.5          # 1 on time / 2 total

    sup2_row = [r for r in result if r["supplier_id"] == "SUP2"][0]
    assert sup2_row["total_shipments"] == 1
    assert sup2_row["delayed_shipments"] == 0
    assert sup2_row["average_delay_days"] == 0.0
    assert sup2_row["on_time_rate"] == 1.0          # 1 on time / 1 total
