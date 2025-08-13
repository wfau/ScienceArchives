import dagster as dg
from pyspark.sql import SparkSession
from dagster import ConfigurableResource


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
            .config(
                "javax.jdo.option.ConnectionURL",
                f"jdbc:derby:;databaseName={self.metastore_uri};create=true",
            )
            .config(
                "javax.jdo.option.ConnectionDriverName",
                "org.apache.derby.jdbc.EmbeddedDriver",
            )
            .config("datanucleus.autoCreateSchema", "true")
            .config("datanucleus.fixedDatastore", "false")
            .config("datanucleus.autoCreateTables", "true")
            .getOrCreate()
        )
