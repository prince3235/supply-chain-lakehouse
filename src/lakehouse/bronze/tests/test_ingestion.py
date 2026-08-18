import pytest
from unittest.mock import MagicMock
import sys; sys.path.append("src/lakehouse/bronze"); from src.ingestion import BronzeIngestionPipeline

def test_bronze_pipeline_init():
    mock_spark = MagicMock()
    pipeline = BronzeIngestionPipeline(mock_spark, "dev", "test-bucket")
    assert pipeline.catalog == "supply_chain_dev"
    assert pipeline.schema == "bronze"
    assert pipeline.raw_prefix == "s3://test-bucket/raw"
    assert pipeline.bronze_prefix == "s3://test-bucket/bronze"

def test_ensure_schema():
    mock_spark = MagicMock()
    pipeline = BronzeIngestionPipeline(mock_spark, "dev", "test-bucket")
    pipeline._ensure_schema()
    
    mock_spark.sql.assert_any_call("CREATE CATALOG IF NOT EXISTS supply_chain_dev")
    mock_spark.sql.assert_any_call("CREATE SCHEMA IF NOT EXISTS supply_chain_dev.bronze")
