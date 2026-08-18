import logging
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, trim, when, upper, row_number
from pyspark.sql.window import Window

logger = logging.getLogger(__name__)

class SilverCleaner:
    """
    Responsible for standardizing nulls, trimming whitespace, and deduplicating records
    before they enter the strict validation stage.
    """
    def __init__(
        self,
        primary_keys: list[str] = None,
        order_by_col: str = "ingestion_timestamp",
        null_literals: list[str] = None
    ):
        self.primary_keys = primary_keys
        self.order_by_col = order_by_col
        # Default null literals if none provided
        self.null_literals = null_literals or ["NULL", "N/A", "NA", "NAN", "NONE", ""]

    def normalize_strings_and_nulls(self, df: DataFrame) -> DataFrame:
        """
        Trims whitespace from string columns.
        Converts configured string null literals into actual SQL NULLs.
        """
        string_cols = [f.name for f in df.schema.fields if f.dataType.typeName() == "string"]
        
        for c in string_cols:
            trimmed_col = trim(col(c))
            upper_col = upper(trimmed_col)
            
            # If the trimmed, upper-cased string is in our null_literals list, convert to NULL.
            # Otherwise, keep the trimmed string.
            df = df.withColumn(
                c,
                when(upper_col.isin(self.null_literals), None).otherwise(trimmed_col)
            )
            
        return df

    def deduplicate(self, df: DataFrame) -> DataFrame:
        """
        Deduplicates records based on primary_keys.
        Keeps the most recent record based on order_by_col.
        """
        if not self.primary_keys:
            logger.info("No primary keys provided; performing global deduplication.")
            return df.dropDuplicates()
            
        if self.order_by_col not in df.columns:
            logger.warning(f"Order by column '{self.order_by_col}' not found. Falling back to global deduplication.")
            return df.dropDuplicates(subset=self.primary_keys)

        logger.info(f"Deduplicating based on primary keys: {self.primary_keys} ordered by {self.order_by_col}")
        
        window_spec = Window.partitionBy(*self.primary_keys).orderBy(col(self.order_by_col).desc())
        
        df_dedup = (df.withColumn("_row_num", row_number().over(window_spec))
                      .filter(col("_row_num") == 1)
                      .drop("_row_num"))
        return df_dedup

    def execute(self, df: DataFrame) -> DataFrame:
        """
        Executes the full cleaning pipeline deterministically.
        """
        logger.info("Starting SilverCleaner execution")
        
        # 1. Normalize strings and nulls
        df_normalized = self.normalize_strings_and_nulls(df)
        
        # 2. Deduplicate
        df_dedup = self.deduplicate(df_normalized)
        
        logger.info("Finished SilverCleaner execution")
        return df_dedup
