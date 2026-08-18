import pytest
import os
import sys
from pyspark.sql import SparkSession

# Ensure the correct Python interpreter is used for the JVM-spawned Python worker
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
os.environ["HADOOP_HOME"] = "C:\\hadoop"
os.environ["PATH"] = "C:\\hadoop\\bin;" + os.environ.get("PATH", "")


@pytest.fixture(scope="session")
def spark_session():
    """
    Creates a local SparkSession for testing Gold layer transformations.
    Uses Arrow-based DataFrame creation to avoid Python worker socket issues
    on Windows + Python 3.12 with PySpark 3.5.x.
    """
    spark = (
        SparkSession.builder
        .master("local[1]")
        .appName("supply-chain-gold-tests")
        .config("spark.sql.shuffle.partitions", "1")
        .config("spark.default.parallelism", "1")
        .config("spark.ui.enabled", "false")
        # Use Arrow to create DataFrames from Pandas — avoids Python worker spawning
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.1.0")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .getOrCreate()
    )
    yield spark
    spark.stop()
