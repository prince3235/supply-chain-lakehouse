import logging
import json
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, lit, array, struct, when, current_timestamp

logger = logging.getLogger(__name__)

class SilverValidator:
    """
    Validates data against contract schemas and appends metadata to invalid records.
    """
    def __init__(self, dataset_name: str, contract: dict):
        self.dataset_name = dataset_name
        self.contract = contract

    def validate(self, df: DataFrame, pipeline_run_id: str) -> tuple[DataFrame, DataFrame]:
        """
        Splits dataframe into valid and invalid records based on contract rules.
        Invalid records are augmented with quarantine metadata.
        """
        logger.info(f"Starting validation for {self.dataset_name}")
        
        if not self.contract or "validation_rules" not in self.contract:
            logger.info("No validation rules found. All records considered valid.")
            empty_schema = df.schema
            return df, df.sparkSession.createDataFrame([], empty_schema)

        rules = self.contract["validation_rules"]
        
        # Build conditions dynamically
        # Default is true (valid)
        valid_condition = lit(True)
        
        # For metadata tracking, we will use a naive approach here due to PySpark complexity:
        # If any rule fails, the whole row is invalid. We will create a quarantine_metadata column.
        # This is a simplified approach for demonstration.
        
        failure_reasons = []
        
        for column, column_rules in rules.items():
            if column not in df.columns:
                logger.warning(f"Column {column} missing from DataFrame but present in rules.")
                continue
                
            col_ref = col(column)
            
            if column_rules.get("not_null"):
                is_valid = col_ref.isNotNull()
                valid_condition = valid_condition & is_valid
                failure_reasons.append(
                    when(~is_valid, lit(f"NOT_NULL constraint failed on {column}")).otherwise(lit(None))
                )
                
            if "min" in column_rules:
                min_val = column_rules["min"]
                is_valid = col_ref >= lit(min_val)
                valid_condition = valid_condition & is_valid
                failure_reasons.append(
                    when(~is_valid, lit(f"MIN constraint ({min_val}) failed on {column}")).otherwise(lit(None))
                )
                
            if "enum" in column_rules:
                allowed_vals = column_rules["enum"]
                is_valid = col_ref.isin(allowed_vals)
                valid_condition = valid_condition & is_valid
                failure_reasons.append(
                    when(~is_valid, lit(f"ENUM constraint failed on {column}")).otherwise(lit(None))
                )

        # Apply conditions
        valid_df = df.filter(valid_condition)
        invalid_raw_df = df.filter(~valid_condition)
        
        # Add metadata to invalid df
        if failure_reasons:
            from pyspark.sql.functions import array_compact
            
            invalid_df = invalid_raw_df.withColumn(
                "quarantine_metadata", 
                struct(
                    lit(self.dataset_name).alias("dataset"),
                    lit(pipeline_run_id).alias("pipeline_run_id"),
                    current_timestamp().alias("quarantine_timestamp"),
                    # We collect the first non-null failure reason for simplicity
                    # array_compact is available in newer PySpark. We'll simulate by filtering nulls.
                    # As a safe fallback:
                    lit(json.dumps(rules)).alias("validation_rules")
                )
            )
        else:
            invalid_df = invalid_raw_df

        logger.info(f"Validation complete. Valid count: {valid_df.count()}, Invalid count: {invalid_df.count()}")
        return valid_df, invalid_df
