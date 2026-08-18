import pytest
import pandas as pd
from src.dimensions import build_dim_product, build_dim_store, build_dim_supplier


def test_build_dim_product(spark_session):
    data = {
        "product_id":   ["P1", "P1", "P2"],
        "product_name": ["Laptop", "Laptop", "Mouse"],
        "category":     ["Electronics", "Electronics", "Electronics"],
        "subcategory":  ["Computers", "Computers", "Accessories"],
        "brand":        ["BrandA", "BrandA", "BrandB"],
        "unit_cost":    [500.0, 500.0, 10.0],
        "selling_price":[800.0, 800.0, 25.0],
    }
    df = spark_session.createDataFrame(pd.DataFrame(data))

    result = build_dim_product(df).collect()

    assert len(result) == 2
    ids = {row["product_id"] for row in result}
    assert ids == {"P1", "P2"}


def test_build_dim_store(spark_session):
    data = {
        "store_id":   ["S1", "S1", "S2"],
        "store_name": ["Store 1", "Store 1", "Store 2"],
        "city":       ["NY", "NY", "LA"],
        "state":      ["NY", "NY", "CA"],
        "region":     ["East", "East", "West"],
        "store_type": ["Retail", "Retail", "Wholesale"],
    }
    df = spark_session.createDataFrame(pd.DataFrame(data))

    result = build_dim_store(df).collect()

    assert len(result) == 2
    ids = {row["store_id"] for row in result}
    assert ids == {"S1", "S2"}


def test_build_dim_supplier(spark_session):
    data = {
        "supplier_id":   ["SUP1", "SUP1", "SUP2"],
        "supplier_name": ["Supplier A", "Supplier A", "Supplier B"],
        "product_id":    ["P1", "P2", "P1"],
    }
    df = spark_session.createDataFrame(pd.DataFrame(data))

    result = build_dim_supplier(df).collect()

    # Supplier dimension should only have unique suppliers
    assert len(result) == 2
    ids = {row["supplier_id"] for row in result}
    assert ids == {"SUP1", "SUP2"}
    assert "product_id" not in result[0].asDict()
