from pyspark.sql import DataFrame
from pyspark.sql.functions import col, sum as _sum, when, lit

def build_inventory_health(silver_inventory_df: DataFrame) -> DataFrame:
    """
    Builds the gold_inventory_health dataset.
    Grain: product x store x warehouse x date
    """
    # Group by product, location (store or warehouse), and snapshot date
    # In Silver, snapshot_timestamp is a timestamp. We cast to date.
    df = silver_inventory_df.withColumn("snapshot_date", col("snapshot_timestamp").cast("date"))
    
    return df.groupBy("product_id", "store_id", "warehouse_id", "snapshot_date").agg(
        _sum("available_quantity").alias("total_available"),
        _sum("reserved_quantity").alias("total_reserved"),
        _sum("safety_stock").alias("current_safety_stock"),
        _sum("reorder_point").alias("current_reorder_point"),
        _sum("inventory_value").alias("total_inventory_value")
    ).withColumn(
        "stockout_risk_indicator",
        when(col("total_available") < col("current_safety_stock"), lit(True)).otherwise(lit(False))
    )
