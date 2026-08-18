import pytest
import pandas as pd
from datetime import datetime
from src.facts import build_fact_sales, build_fact_inventory, build_fact_shipments


def test_build_fact_sales(spark_session):
    data = {
        "transaction_id":        ["TX1", "TX2"],
        "transaction_timestamp": [datetime(2026, 8, 1), datetime(2026, 8, 2)],
        "product_id":    ["P1", "P2"],
        "store_id":      ["S1", "S2"],
        "customer_id":   ["C1", "C2"],
        "quantity":      [2, 1],
        "unit_price":    [10.0, 5.0],
        "discount_amount": [0.0, 1.0],
        "total_amount":  [20.0, 4.0],
    }
    df = spark_session.createDataFrame(pd.DataFrame(data))

    result = build_fact_sales(df).collect()

    assert len(result) == 2
    assert "transaction_date" in result[0].asDict()


def test_build_fact_inventory(spark_session):
    data = {
        "inventory_id":        ["INV1", "INV2"],
        "product_id":          ["P1", "P1"],
        "store_id":            ["S1", None],
        "warehouse_id":        [None, "W1"],
        "snapshot_timestamp":  [datetime(2026, 8, 1), datetime(2026, 8, 1)],
        "available_quantity":  [100, 500],
        "reserved_quantity":   [10, 50],
        "reorder_point":       [20, 100],
        "safety_stock":        [30, 150],
        "inventory_value":     [1000.0, 5000.0],
    }
    df = spark_session.createDataFrame(pd.DataFrame(data))

    result = build_fact_inventory(df).collect()

    assert len(result) == 2
    assert "inventory_id" in result[0].asDict()


def test_build_fact_shipments(spark_session):
    data = {
        "shipment_id":           ["SHP1"],
        "supplier_id":           ["SUP1"],
        "product_id":            ["P1"],
        "warehouse_id":          ["W1"],
        "order_date":            [datetime(2026, 8, 1)],
        "expected_delivery_date":[datetime(2026, 8, 5)],
        "actual_delivery_date":  [datetime(2026, 8, 6)],
        "quantity":              [100],
        "status":                ["DELIVERED"],
        "delay_days":            [1],
    }
    df = spark_session.createDataFrame(pd.DataFrame(data))

    result = build_fact_shipments(df).collect()

    assert len(result) == 1
    assert result[0]["delay_days"] == 1
