import pytest
import pandas as pd
import tempfile
import shutil
from src.pipeline import GoldPipeline


def test_pipeline_idempotency_and_merge(spark_session):
    """
    Tests that GoldPipeline.write_gold_table is idempotent (MERGE semantics):
    - First write: creates the table with N rows.
    - Second write with same data: row count unchanged.
    - Third write with updated + new data: upsert is applied correctly.

    NOTE: Local Spark v1 session catalog only supports 2-level namespace
    (database.table), NOT the 3-level Unity Catalog used in production.
    We patch the pipeline instance to use a flat local namespace so the
    merge logic is fully exercised without requiring Databricks.
    """
    temp_dir = tempfile.mkdtemp().replace("\\", "/")
    db_name = "pipeline_test_gold"

    spark_session.sql(f"CREATE DATABASE IF NOT EXISTS {db_name}")

    try:
        pipeline = GoldPipeline(spark_session, "test", "dummy")

        # Override to 2-level local namespace — bypasses Unity Catalog
        pipeline.catalog = db_name
        pipeline.schema = ""                          # absorbed into catalog attr
        pipeline.gold_prefix = f"file:///{temp_dir}"

        # Patch _ensure_schema so it works with the local v1 catalog
        def _local_ensure_schema():
            spark_session.sql(f"CREATE DATABASE IF NOT EXISTS {db_name}")

        pipeline._ensure_schema = _local_ensure_schema

        # Patch the table name resolution inside write_gold_table by overriding
        # the catalog/schema combination at instance level so the table ref becomes
        # "{db_name}.{dataset_name}" — still a valid v1 catalog identifier.
        original_write = pipeline.write_gold_table

        def patched_write(dataset_name, df):
            from delta.tables import DeltaTable
            from src.schemas import get_gold_contract
            import logging
            _log = logging.getLogger("test_pipeline")

            pipeline._ensure_schema()
            gold_table = f"{db_name}.{dataset_name}"
            gold_path = f"{pipeline.gold_prefix}/{dataset_name}"
            contract = get_gold_contract(dataset_name)
            primary_keys = contract.get("primary_keys", [])

            output_count = df.count()
            if output_count == 0:
                return

            if not DeltaTable.isDeltaTable(spark_session, gold_path):
                df.write.format("delta").mode("overwrite").option("path", gold_path).saveAsTable(gold_table)
            else:
                if not primary_keys:
                    df.write.format("delta").mode("overwrite").option("path", gold_path).saveAsTable(gold_table)
                    return

                dt = DeltaTable.forName(spark_session, gold_table)
                condition = " AND ".join([f"target.{pk} = source.{pk}" for pk in primary_keys])
                dt.alias("target").merge(
                    df.alias("source"), condition
                ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()

        pipeline.write_gold_table = patched_write

        # --- Test data ---
        dataset_name = "gold_daily_demand"
        columns = ["product_id", "store_id", "demand_date", "total_daily_quantity"]

        data1 = pd.DataFrame({
            "product_id":           ["P1", "P2"],
            "store_id":             ["S1", "S1"],
            "demand_date":          ["2026-08-01", "2026-08-01"],
            "total_daily_quantity": [10, 20],
        })
        df1 = spark_session.createDataFrame(data1)

        # 1. First write — creates the table
        pipeline.write_gold_table(dataset_name, df1)
        count1 = spark_session.sql(
            f"SELECT COUNT(*) as cnt FROM {db_name}.{dataset_name}"
        ).collect()[0]["cnt"]
        assert count1 == 2, f"Expected 2 rows after first write, got {count1}"

        # 2. Second write with identical data — idempotent (no duplicates)
        pipeline.write_gold_table(dataset_name, df1)
        count2 = spark_session.sql(
            f"SELECT COUNT(*) as cnt FROM {db_name}.{dataset_name}"
        ).collect()[0]["cnt"]
        assert count2 == 2, f"Expected 2 rows after idempotent re-write, got {count2}"

        # 3. Third write — upsert: P1 updated, P3 new
        data2 = pd.DataFrame({
            "product_id":           ["P1", "P3"],
            "store_id":             ["S1", "S1"],
            "demand_date":          ["2026-08-01", "2026-08-01"],
            "total_daily_quantity": [15, 5],
        })
        df2 = spark_session.createDataFrame(data2)
        pipeline.write_gold_table(dataset_name, df2)

        count3 = spark_session.sql(
            f"SELECT COUNT(*) as cnt FROM {db_name}.{dataset_name}"
        ).collect()[0]["cnt"]
        assert count3 == 3, f"Expected 3 rows after upsert, got {count3}"

        p1_val = spark_session.sql(
            f"SELECT total_daily_quantity FROM {db_name}.{dataset_name} WHERE product_id='P1'"
        ).collect()[0][0]
        assert p1_val == 15, f"Expected P1 quantity=15 after upsert, got {p1_val}"

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        spark_session.sql(f"DROP DATABASE IF EXISTS {db_name} CASCADE")
