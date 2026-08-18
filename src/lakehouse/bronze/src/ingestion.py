import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, input_file_name, lit, col
from delta.tables import DeltaTable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BronzeIngestionPipeline:
    def __init__(self, spark: SparkSession, env: str, bucket_name: str):
        self.spark = spark
        self.catalog = f"supply_chain_{env}"
        self.schema = "bronze"
        self.bucket = bucket_name
        self.raw_prefix = f"s3://{self.bucket}/raw"
        self.bronze_prefix = f"s3://{self.bucket}/bronze"
        self.checkpoint_prefix = f"s3://{self.bucket}/checkpoints/bronze"

    def _ensure_schema(self):
        self.spark.sql(f"CREATE CATALOG IF NOT EXISTS {self.catalog}")
        self.spark.sql(f"CREATE SCHEMA IF NOT EXISTS {self.catalog}.{self.schema}")

    def ingest_dataset(self, dataset_name: str, format: str = "parquet", primary_keys: list = None, partition_cols: list = None):
        """
        Ingest raw data incrementally using Auto Loader and merge into Delta Lake idempotently.
        """
        self._ensure_schema()
        table_name = f"{self.catalog}.{self.schema}.{dataset_name}"
        source_path = f"{self.raw_prefix}/{dataset_name}/"
        checkpoint_path = f"{self.checkpoint_prefix}/{dataset_name}/"
        
        logger.info(f"Starting Bronze ingestion for {dataset_name} into {table_name}")

        # Check if table exists
        table_exists = self.spark._jsparkSession.catalog().tableExists(table_name)
        
        # Read stream using Auto Loader
        raw_df = (self.spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", format)
            .option("cloudFiles.schemaLocation", checkpoint_path + "schema")
            .option("cloudFiles.inferColumnTypes", "true")
            .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
            .load(source_path)
            .withColumn("_ingestion_timestamp", current_timestamp())
            .withColumn("_source_file", input_file_name())
        )

        def upsert_to_delta(microBatchOutputDF, batchId):
            microBatchOutputDF.persist()
            count = microBatchOutputDF.count()
            if count == 0:
                microBatchOutputDF.unpersist()
                return
                
            logger.info(f"Processing batch {batchId} for {dataset_name} with {count} records")
            
            microBatchOutputDF = microBatchOutputDF.withColumn("_batch_id", lit(batchId))
            
            if not DeltaTable.isDeltaTable(self.spark, f"{self.bronze_prefix}/{dataset_name}"):
                # First run, write and create table
                writer = microBatchOutputDF.write.format("delta").mode("append")
                if partition_cols:
                    writer = writer.partitionBy(partition_cols)
                writer.saveAsTable(table_name)
            else:
                # Upsert using source file and/or primary keys for idempotency
                dt = DeltaTable.forName(self.spark, table_name)
                
                if primary_keys:
                    condition = " AND ".join([f"target.{pk} = source.{pk}" for pk in primary_keys])
                else:
                    # Fallback to source file level idempotency
                    condition = "target._source_file = source._source_file"
                    
                dt.alias("target").merge(
                    microBatchOutputDF.alias("source"),
                    condition
                ).whenNotMatchedInsertAll().execute()
            
            microBatchOutputDF.unpersist()

        # Execute the stream with availableNow
        query = (raw_df.writeStream
            .foreachBatch(upsert_to_delta)
            .option("checkpointLocation", checkpoint_path)
            .trigger(availableNow=True)
            .start()
        )
        
        query.awaitTermination()
        logger.info(f"Finished Bronze ingestion for {dataset_name}")
