import logging
from pyspark.sql import DataFrame, SparkSession
from delta.tables import DeltaTable
from src.schemas import get_gold_contract

logger = logging.getLogger(__name__)

class GoldPipeline:
    """
    Orchestrates the safe, idempotent publishing of Gold datasets.
    """
    def __init__(self, spark: SparkSession, env: str, bucket_name: str):
        self.spark = spark
        self.catalog = f"supply_chain_{env}"
        self.schema = "gold"
        self.gold_prefix = f"s3://{bucket_name}/gold"

    def _ensure_schema(self):
        try:
            self.spark.sql(f"CREATE CATALOG IF NOT EXISTS {self.catalog}")
            self.spark.sql(f"CREATE SCHEMA IF NOT EXISTS {self.catalog}.{self.schema}")
        except Exception as e:
            logger.error(f"Failed to ensure schema: {e}")
            pass

    def write_gold_table(self, dataset_name: str, df: DataFrame):
        """
        Upserts the aggregated dataframe into the Gold layer Delta table using MERGE.
        """
        self._ensure_schema()
        
        gold_table = f"{self.catalog}.{self.schema}.{dataset_name}"
        gold_path = f"{self.gold_prefix}/{dataset_name}"
        contract = get_gold_contract(dataset_name)
        primary_keys = contract.get("primary_keys", [])
        
        output_count = df.count()
        logger.info(f"Writing {output_count} records to Gold table {gold_table}")
        
        if output_count == 0:
            logger.info("No records to write. Skipping.")
            return

        try:
            if not DeltaTable.isDeltaTable(self.spark, gold_path):
                logger.info(f"Creating Gold table {gold_table}")
                df.write.format("delta").mode("overwrite").option("path", gold_path).saveAsTable(gold_table)
            else:
                if not primary_keys:
                    logger.warning(f"No primary keys for {dataset_name}. Performing full overwrite!")
                    df.write.format("delta").mode("overwrite").option("path", gold_path).saveAsTable(gold_table)
                    return
                
                logger.info(f"Merging Gold table {gold_table} on keys {primary_keys}")
                dt = DeltaTable.forName(self.spark, gold_table)
                condition = " AND ".join([f"target.{pk} = source.{pk}" for pk in primary_keys])
                
                dt.alias("target").merge(
                    df.alias("source"),
                    condition
                ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
                
            logger.info(f"Successfully updated Gold table {gold_table}")
        except Exception as e:
            logger.error(f"Failed to write to Gold table {gold_table}: {e}")
            raise
