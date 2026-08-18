from pyspark.sql import DataFrame
from pyspark.sql.functions import col

def build_fact_sales(silver_sales_df: DataFrame) -> DataFrame:
    """
    Transforms Silver sales into Gold fact_sales.
    Grain: transaction_line
    """
    return silver_sales_df.select(
        col("transaction_id"),
        col("transaction_timestamp").alias("transaction_date"), # Truncated to date usually in DWH
        col("product_id"),
        col("store_id"),
        col("customer_id"),
        col("quantity"),
        col("unit_price"),
        col("discount_amount"),
        col("total_amount")
    )

def build_fact_inventory(silver_inventory_df: DataFrame) -> DataFrame:
    """
    Transforms Silver inventory into Gold fact_inventory.
    Grain: product x location x timestamp
    """
    return silver_inventory_df.select(
        col("inventory_id"),
        col("product_id"),
        col("store_id"),
        col("warehouse_id"),
        col("snapshot_timestamp"),
        col("available_quantity"),
        col("reserved_quantity"),
        col("reorder_point"),
        col("safety_stock"),
        col("inventory_value")
    )

def build_fact_shipments(silver_shipments_df: DataFrame) -> DataFrame:
    """
    Transforms Silver shipments into Gold fact_shipments.
    Grain: shipment
    """
    return silver_shipments_df.select(
        col("shipment_id"),
        col("supplier_id"),
        col("product_id"),
        col("warehouse_id"),
        col("order_date"),
        col("expected_delivery_date"),
        col("actual_delivery_date"),
        col("quantity"),
        col("status"),
        col("delay_days")
    )
