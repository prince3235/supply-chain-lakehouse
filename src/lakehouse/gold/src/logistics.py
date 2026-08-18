from pyspark.sql import DataFrame
from pyspark.sql.functions import col, sum as _sum, count, when, lit

def build_shipment_performance(silver_shipments_df: DataFrame) -> DataFrame:
    """
    Builds the gold_shipment_performance dataset.
    Grain: warehouse x delivery_date
    """
    # Use expected delivery date as the grain date to align planning
    df = silver_shipments_df.withColumn("delivery_date", col("expected_delivery_date"))
    
    return df.groupBy("warehouse_id", "delivery_date").agg(
        count("shipment_id").alias("incoming_shipments"),
        _sum("quantity").alias("incoming_quantity"),
        _sum(when(col("delay_days") > 0, lit(1)).otherwise(lit(0))).alias("delayed_shipments")
    )
