from pyspark.sql import DataFrame
from pyspark.sql.functions import col, sum as _sum

def build_daily_demand(silver_sales_df: DataFrame) -> DataFrame:
    """
    Builds the gold_daily_demand dataset.
    Grain: product x store x date
    """
    df = silver_sales_df.withColumn("demand_date", col("transaction_timestamp").cast("date"))
    
    return df.groupBy("product_id", "store_id", "demand_date").agg(
        _sum("quantity").alias("total_daily_quantity"),
        _sum("total_amount").alias("total_daily_revenue")
    )
