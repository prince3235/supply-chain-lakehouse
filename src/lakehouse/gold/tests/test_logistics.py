import pytest
import pandas as pd
from datetime import datetime
from src.logistics import build_shipment_performance


def test_build_shipment_performance(spark_session):
    data = {
        "shipment_id": ["SHP1", "SHP2", "SHP3"],
        "supplier_id": ["SUP1", "SUP2", "SUP2"],
        "product_id":  ["P1",   "P2",   "P2"],
        "warehouse_id":["W1",   "W1",   "W2"],
        "order_date":  [datetime(2026, 8, 1), datetime(2026, 8, 2), datetime(2026, 8, 1)],
        "expected_delivery_date": [datetime(2026, 8, 5), datetime(2026, 8, 5), datetime(2026, 8, 5)],
        "actual_delivery_date":   [datetime(2026, 8, 6), datetime(2026, 8, 5), datetime(2026, 8, 5)],
        "quantity":    [100, 50, 200],
        "status":      ["DELIVERED", "DELIVERED", "DELIVERED"],
        "delay_days":  [1, 0, 0],
    }
    df = spark_session.createDataFrame(pd.DataFrame(data))

    result_df = build_shipment_performance(df)
    result = result_df.collect()

    assert len(result) == 2

    w1_row = [r for r in result if r["warehouse_id"] == "W1"][0]
    assert w1_row["incoming_shipments"] == 2
    assert w1_row["incoming_quantity"] == 150
    assert w1_row["delayed_shipments"] == 1

    w2_row = [r for r in result if r["warehouse_id"] == "W2"][0]
    assert w2_row["incoming_shipments"] == 1
    assert w2_row["incoming_quantity"] == 200
    assert w2_row["delayed_shipments"] == 0
