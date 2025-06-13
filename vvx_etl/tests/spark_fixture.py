import pytest
from pyspark.sql import SparkSession
from pathlib import Path


@pytest.fixture(scope="module")
def spark_fixture(tmp_path_factory):
    """Provide a Spark session with a unique temp warehouse per session."""
    warehouse_dir = tmp_path_factory.mktemp("spark_warehouse")
    warehouse_path = str(warehouse_dir)

    spark = (
        SparkSession.builder.appName("TestSparkSession")
        .master("local[4]")
        .config("spark.driver.memory", "30g")
        .config("spark.sql.warehouse.dir", warehouse_path)
        .config("spark.sql.catalogImplementation", "hive")
        .config(
            "javax.jdo.option.ConnectionURL",
            f"jdbc:derby:{warehouse_path}/metastore_db;create=true",
        )
        .enableHiveSupport()
        .getOrCreate()
    )

    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)
    spark.sql("CREATE DATABASE IF NOT EXISTS default")

    yield spark

    spark.stop()
