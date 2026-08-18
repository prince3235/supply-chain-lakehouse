from pyspark.sql import DataFrame
from pyspark.sql.functions import col, trim, when, upper
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number

class SilverCleaner:
    def __init__(self, primary_keys: list[str] = None, order_by_col: str = "_ingestion_timestamp"):
        """
        :param primary_keys: List of columns that uniquely identify a record for deduplication.
        :param order_by_col: Column to use for ordering during deduplication (keep the latest).
        """
        self.primary_keys = primary_keys
        self.order_by_col = order_by_col

    def standardize_nulls_and_strings(self, df: DataFrame) -> DataFrame:
        """
        Trims all string columns and converts explicit 'NULL', 'N/A' strings to actual SQL NULLs.
        """
        string_cols = [f.name for f in df.schema.fields if f.dataType.typeName() == "string"]
        
        for c in string_cols:
            df = df.withColumn(
                c, 
                when(upper(trim(col(c))).isin("NULL", "N/A", "NAN", ""), None)
                .otherwise(trim(col(c)))
            )
        return df

    def deduplicate(self, df: DataFrame) -> DataFrame:
        """
        Deduplicates records based on primary_keys, keeping the most recent based on order_by_col.
        If no primary keys are provided, it performs a simple dropDuplicates.
        """
        if not self.primary_keys:
            return df.dropDuplicates()
            
        # Deduplicate by primary key keeping the latest record
        window_spec = Window.partitionBy(*self.primary_keys).orderBy(col(self.order_by_col).desc())
        
        df_dedup = (df.withColumn("_row_num", row_number().over(window_spec))
                    .filter(col("_row_num") == 1)
                    .drop("_row_num"))
        return df_dedup

    def clean(self, df: DataFrame) -> DataFrame:
        """
        Main entry point to apply all cleaning steps.
        """
        df_clean = self.standardize_nulls_and_strings(df)
        df_dedup = self.deduplicate(df_clean)
        return df_dedup
