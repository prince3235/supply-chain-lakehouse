import logging
from pyspark.sql import SparkSession
from src.cleaner import SilverCleaner
from src.validator import SilverValidator
from delta.tables import DeltaTable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SilverPipeline:
    def __init__(self, spark: SparkSession, env: str, bucket_name: str):
        self.spark = spark
        self.catalog = f"supply_chain_{env}"
        self.schema = "silver"
        self.bucket = bucket_name
        self.bronze_prefix = f"s3://{self.bucket}/bronze"
        self.silver_prefix = f"s3://{self.bucket}/silver"
        self.quarantine_prefix = f"s3://{self.bucket}/quarantine/silver"

    def _ensure_schema(self):
        self.spark.sql(f"CREATE CATALOG IF NOT EXISTS {self.catalog}")
        self.spark.sql(f"CREATE SCHEMA IF NOT EXISTS {self.catalog}.{self.schema}")

    def process(self, dataset_name: str, primary_keys: list[str] = None, validation_rules: dict = None):
        """
        Reads from Bronze, cleans, validates, and writes to Silver and Quarantine.
        In a real production system, this could read incrementally using spark.readStream.
        """
        self._ensure_schema()
        
        bronze_table = f"{self.catalog}.bronze.{dataset_name}"
        silver_table = f"{self.catalog}.{self.schema}.{dataset_name}"
        
        logger.info(f"Starting Silver processing for {dataset_name}")
        
        # Check if source exists
        if not self.spark._jsparkSession.catalog().tableExists(bronze_table):
            logger.warning(f"Bronze table {bronze_table} does not exist. Skipping.")
            return
            
        df = self.spark.table(bronze_table)
        
        # 1. Clean
        cleaner = SilverCleaner(primary_keys=primary_keys)
        df_cleaned = cleaner.clean(df)
        
        # 2. Validate
        validator = SilverValidator(constraints=validation_rules)
        valid_df, invalid_df = validator.validate(df_cleaned)
        
        # 3. Write Invalid to Quarantine
        invalid_count = invalid_df.count()
        if invalid_count > 0:
            logger.warning(f"Found {invalid_count} invalid records for {dataset_name}. Writing to quarantine.")
            invalid_df.write.format("delta").mode("append").save(f"{self.quarantine_prefix}/{dataset_name}")
            
        # 4. Write Valid to Silver
        valid_count = valid_df.count()
        if valid_count > 0:
            logger.info(f"Writing {valid_count} valid records to {silver_table}")
            
            if not DeltaTable.isDeltaTable(self.spark, f"{self.silver_prefix}/{dataset_name}"):
                valid_df.write.format("delta").mode("overwrite").saveAsTable(silver_table)
            else:
                dt = DeltaTable.forName(self.spark, silver_table)
                
                if primary_keys:
                    condition = " AND ".join([f"target.{pk} = source.{pk}" for pk in primary_keys])
                    dt.alias("target").merge(
                        valid_df.alias("source"),
                        condition
                    ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
                else:
                    # Append fallback
                    valid_df.write.format("delta").mode("append").saveAsTable(silver_table)
        
        logger.info(f"Finished Silver processing for {dataset_name}")
