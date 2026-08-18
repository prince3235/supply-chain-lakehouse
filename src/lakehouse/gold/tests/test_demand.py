import pytest
import pandas as pd
from datetime import datetime
from src.demand import build_daily_demand


def test_build_daily_demand(spark_session):
    data = {
        "transaction_id":        ["TX1", "TX2", "TX3"],
        "transaction_timestamp": [datetime(2026, 8, 1, 10, 0),
                                  datetime(2026, 8, 1, 15, 0),
                                  datetime(2026, 8, 1, 12, 0)],
        "product_id":    ["P1", "P1", "P2"],
        "store_id":      ["S1", "S1", "S1"],
        "customer_id":   ["C1", "C2", "C3"],
        "quantity":      [2, 3, 1],
        "unit_price":    [10.0, 10.0, 5.0],
        "discount_amount": [0.0, 0.0, 0.0],
        "total_amount":  [20.0, 30.0, 5.0],
    }
    df = spark_session.createDataFrame(pd.DataFrame(data))

    result_df = build_daily_demand(df)
    result = result_df.collect()

    assert len(result) == 2

    p1_row = [r for r in result if r["product_id"] == "P1"][0]
    assert p1_row["total_daily_quantity"] == 5   # 2 + 3
    assert p1_row["total_daily_revenue"] == 50.0  # 20.0 + 30.0

    p2_row = [r for r in result if r["product_id"] == "P2"][0]
    assert p2_row["total_daily_quantity"] == 1
    assert p2_row["total_daily_revenue"] == 5.0
