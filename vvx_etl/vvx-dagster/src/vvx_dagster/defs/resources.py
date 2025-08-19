import dagster as dg
from pyspark.sql import SparkSession
from dagster import ConfigurableResource
from dotenv import load_dotenv
import os

load_dotenv("../../docker/.env")
POSTGRES_URL = os.getenv("HIVE_JDBC_URL")
POSTGRES_USER = os.getenv("HIVE_DB_USER")
POSTGRES_PASS = os.getenv("HIVE_DB_PASS")


class SparkResource(dg.ConfigurableResource):
    metastore_uri: str
    warehouse_dir: str
    cores: int
    memory: str

    def get_session(self) -> SparkSession:
        return (
            SparkSession.builder.appName("dagster_spark_asset")
            .master("local[*]")
            .config("spark.cores.max", self.cores)
            .config("spark.driver.memory", self.memory)
            .enableHiveSupport()
            .config("spark.sql.warehouse.dir", self.warehouse_dir)
            .config("spark.sql.warehouse.dir", "/opt/spark/warehouse")
            .config(
                "javax.jdo.option.ConnectionURL",
                "jdbc:postgresql://postgres:5432/hive_metastore",
            )
            .config("javax.jdo.option.ConnectionURL", POSTGRES_URL)
            .config("javax.jdo.option.ConnectionUserName", POSTGRES_USER)
            .config("javax.jdo.option.ConnectionPassword", POSTGRES_PASS)
            .config("spark.jars.packages", "org.postgresql:postgresql:42.6.0")
            .getOrCreate()
        )
