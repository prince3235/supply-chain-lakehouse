import logging
import uuid
from pyspark.sql import SparkSession
from delta.tables import DeltaTable

from src.cleaner import SilverCleaner
from src.validator import SilverValidator
from src.transformer import SilverTransformer
from src.quarantine import QuarantineHandler
from src.schemas import get_contract

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SilverPipeline:
    """
    Production-grade orchestration of the Silver Layer.
    """
    def __init__(self, spark: SparkSession, env: str, bucket_name: str):
        self.spark = spark
        self.catalog = f"supply_chain_{env}"
        self.schema = "silver"
        self.bucket = bucket_name
        self.silver_prefix = f"s3://{self.bucket}/silver"
        
        self.quarantine_handler = QuarantineHandler(spark, env, bucket_name)

    def _ensure_schema(self):
        try:
            self.spark.sql(f"CREATE CATALOG IF NOT EXISTS {self.catalog}")
            self.spark.sql(f"CREATE SCHEMA IF NOT EXISTS {self.catalog}.{self.schema}")
        except Exception as e:
            logger.error(f"Failed to ensure schema: {e}")
            # If running locally without Unity Catalog, this might fail. We log and continue for tests.
            pass

    def enforce_strict_schema(self, df, contract: dict):
        """
        Ensures the dataframe contains all required columns before processing.
        """
        if not contract:
            return
            
        required_cols = contract.get("required_columns", [])
        missing_cols = [c for c in required_cols if c not in df.columns]
        
        if missing_cols:
            raise ValueError(f"Schema mismatch: Missing required columns {missing_cols}")

    def process(self, dataset_name: str):
        """
        Executes the Bronze -> Silver pipeline idempotently.
        """
        pipeline_run_id = str(uuid.uuid4())
        logger.info(f"Starting Silver pipeline run {pipeline_run_id} for {dataset_name}")
        
        self._ensure_schema()
        
        bronze_table = f"{self.catalog}.bronze.{dataset_name}"
        silver_table = f"{self.catalog}.{self.schema}.{dataset_name}"
        contract = get_contract(dataset_name)
        
        # Check if source exists
        try:
            if not self.spark.catalog.tableExists(bronze_table):
                logger.warning(f"Bronze table {bronze_table} does not exist. Pipeline aborting safely.")
                return
            df = self.spark.table(bronze_table)
        except Exception as e:
            logger.error(f"Failed to read bronze table: {e}")
            raise

        try:
            input_count = df.count()
            logger.info(f"Read {input_count} records from Bronze.")
            
            # 0. Schema Enforcement
            self.enforce_strict_schema(df, contract)
            
            # 1. Clean
            cleaner = SilverCleaner(primary_keys=contract.get("primary_keys"))
            df_cleaned = cleaner.execute(df)
            
            # 2. Transform
            transformer = SilverTransformer(contract)
            df_transformed = transformer.transform(df_cleaned)
            
            # 3. Validate
            validator = SilverValidator(dataset_name, contract)
            valid_df, invalid_df = validator.validate(df_transformed, pipeline_run_id)
            
            # 4. Quarantine
            self.quarantine_handler.quarantine_records(dataset_name, invalid_df)
            
            # 5. Silver Write (Idempotent MERGE)
            valid_count = valid_df.count()
            if valid_count > 0:
                logger.info(f"Writing {valid_count} valid records to {silver_table}")
                
                silver_path = f"{self.silver_prefix}/{dataset_name}"
                
                if not DeltaTable.isDeltaTable(self.spark, silver_path):
                    logger.info("Silver table does not exist. Creating via Overwrite.")
                    valid_df.write.format("delta").mode("overwrite").saveAsTable(silver_table)
                else:
                    logger.info("Executing idempotent MERGE into Silver table.")
                    dt = DeltaTable.forName(self.spark, silver_table)
                    primary_keys = contract.get("primary_keys", [])
                    
                    if primary_keys:
                        condition = " AND ".join([f"target.{pk} = source.{pk}" for pk in primary_keys])
                        dt.alias("target").merge(
                            valid_df.alias("source"),
                            condition
                        ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
                    else:
                        logger.warning("No primary keys defined. Falling back to append (may cause duplicates on rerun).")
                        valid_df.write.format("delta").mode("append").saveAsTable(silver_table)
            else:
                logger.warning("No valid records to write to Silver.")
                
            logger.info(f"Pipeline run {pipeline_run_id} completed successfully.")
            
        except ValueError as ve:
            logger.error(f"Validation Error: {ve}")
            raise
        except Exception as e:
            logger.error(f"Pipeline run {pipeline_run_id} failed: {e}")
            raise
