from pyspark.sql import DataFrame
from pyspark.sql.functions import col

def build_dim_product(silver_products_df: DataFrame) -> DataFrame:
    """
    Transforms Silver products into Gold dim_product.
    Grain: product
    """
    return silver_products_df.select(
        col("product_id"),
        col("product_name"),
        col("category"),
        col("subcategory"),
        col("brand"),
        col("unit_cost"),
        col("selling_price")
    ).dropDuplicates(["product_id"])

def build_dim_store(silver_stores_df: DataFrame) -> DataFrame:
    """
    Transforms Silver stores into Gold dim_store.
    Grain: store
    """
    return silver_stores_df.select(
        col("store_id"),
        col("store_name"),
        col("city"),
        col("state"),
        col("region"),
        col("store_type")
    ).dropDuplicates(["store_id"])

def build_dim_supplier(silver_suppliers_df: DataFrame) -> DataFrame:
    """
    Transforms Silver suppliers into Gold dim_supplier.
    Grain: supplier
    """
    # Suppliers in Silver is Supplier X Product.
    # To get dim_supplier at the Supplier grain, we aggregate or take distinct.
    return silver_suppliers_df.select(
        col("supplier_id"),
        col("supplier_name")
    ).dropDuplicates(["supplier_id"])
