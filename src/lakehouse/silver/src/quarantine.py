import logging
from pyspark.sql import DataFrame
from pyspark.sql import SparkSession

logger = logging.getLogger(__name__)

class QuarantineHandler:
    """
    Handles appending invalid records to the quarantine Delta lake safely.
    """
    def __init__(self, spark: SparkSession, env: str, bucket_name: str):
        self.spark = spark
        self.quarantine_prefix = f"s3://{bucket_name}/quarantine/silver"

    def quarantine_records(self, dataset_name: str, invalid_df: DataFrame):
        """
        Writes invalid records to quarantine incrementally.
        In a production scenario with streaming, this would use writeStream.
        """
        invalid_count = invalid_df.count()
        if invalid_count == 0:
            logger.info(f"No invalid records to quarantine for {dataset_name}.")
            return

        quarantine_path = f"{self.quarantine_prefix}/{dataset_name}"
        logger.warning(f"Quarantining {invalid_count} records to {quarantine_path}")

        try:
            # We use append mode. Duplicates are acceptable in quarantine if a pipeline
            # is blindly rerun without primary key tracking in quarantine itself, 
            # but ideally pipeline_run_id distinguishes them.
            invalid_df.write.format("delta").mode("append").save(quarantine_path)
            logger.info("Quarantine write successful.")
        except Exception as e:
            logger.error(f"Failed to write to quarantine: {e}")
            raise
