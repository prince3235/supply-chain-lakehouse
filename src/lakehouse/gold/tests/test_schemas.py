import pytest
from pyspark.sql.types import StringType, StructType, StructField
from src.schemas import get_gold_contract

def test_dim_product_schema_contract(spark_session):
    contract = get_gold_contract("dim_product")
    assert contract["primary_keys"] == ["product_id"]
    assert contract["grain"] == "product"

def test_dim_store_schema_contract(spark_session):
    contract = get_gold_contract("dim_store")
    assert contract["primary_keys"] == ["store_id"]
    assert contract["grain"] == "store"

def test_gold_daily_demand_schema_contract(spark_session):
    contract = get_gold_contract("gold_daily_demand")
    assert contract["primary_keys"] == ["product_id", "store_id", "demand_date"]
    assert contract["grain"] == "product_store_date"

def test_gold_inventory_health_schema_contract(spark_session):
    contract = get_gold_contract("gold_inventory_health")
    assert contract["primary_keys"] == ["product_id", "store_id", "warehouse_id", "snapshot_date"]
    assert contract["grain"] == "product_location_date"

def test_gold_supplier_performance_schema_contract(spark_session):
    contract = get_gold_contract("gold_supplier_performance")
    assert contract["primary_keys"] == ["supplier_id", "performance_period"]
    assert contract["grain"] == "supplier_period"
