import pytest
from pyspark.sql import SparkSession
from src.cleaner import SilverCleaner
from datetime import datetime

@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.master("local[1]").appName("SilverTests").getOrCreate()

def test_standardize_nulls_and_strings(spark):
    data = [
        (" 123 ", "N/A"),
        ("abc", "NULL"),
        (" def", "nan "),
        ("ghi", ""),
        ("jkl", "valid")
    ]
    df = spark.createDataFrame(data, ["col1", "col2"])
    
    cleaner = SilverCleaner()
    cleaned_df = cleaner.standardize_nulls_and_strings(df)
    results = cleaned_df.collect()
    
    assert results[0]["col1"] == "123"
    assert results[0]["col2"] is None
    
    assert results[1]["col1"] == "abc"
    assert results[1]["col2"] is None
    
    assert results[2]["col1"] == "def"
    assert results[2]["col2"] is None
    
    assert results[3]["col1"] == "ghi"
    assert results[3]["col2"] is None
    
    assert results[4]["col1"] == "jkl"
    assert results[4]["col2"] == "valid"

def test_deduplicate(spark):
    data = [
        (1, "A", datetime(2023, 1, 1, 10, 0)),
        (1, "B", datetime(2023, 1, 1, 12, 0)), # Latest for id=1
        (2, "C", datetime(2023, 1, 1, 9, 0)),
        (2, "C", datetime(2023, 1, 1, 9, 0))   # Exact duplicate
    ]
    df = spark.createDataFrame(data, ["id", "val", "_ingestion_timestamp"])
    
    cleaner = SilverCleaner(primary_keys=["id"])
    dedup_df = cleaner.deduplicate(df)
    results = dedup_df.orderBy("id").collect()
    
    assert len(results) == 2
    assert results[0]["id"] == 1
    assert results[0]["val"] == "B" # Kept the latest
    assert results[1]["id"] == 2
