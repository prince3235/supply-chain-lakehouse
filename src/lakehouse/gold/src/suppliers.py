from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count, sum as _sum, avg, when, lit, date_trunc

def build_supplier_performance(silver_shipments_df: DataFrame) -> DataFrame:
    """
    Builds the gold_supplier_performance dataset.
    Grain: supplier x performance_period (monthly)
    """
    df = silver_shipments_df.withColumn("performance_period", date_trunc("month", col("expected_delivery_date")))
    
    return df.groupBy("supplier_id", "performance_period").agg(
        count("shipment_id").alias("total_shipments"),
        _sum(when(col("delay_days") > 0, lit(1)).otherwise(lit(0))).alias("delayed_shipments"),
        avg("delay_days").alias("average_delay_days")
    ).withColumn(
        "on_time_rate",
        (col("total_shipments") - col("delayed_shipments")) / col("total_shipments")
    )
