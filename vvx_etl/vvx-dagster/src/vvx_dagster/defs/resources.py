from dagster import resource
from pyspark.sql import SparkSession

metastore_location = "/tmp/spark-hive-metastore"


@resource
def spark(_):
    return (
        SparkSession.builder.appName("dagster_spark_asset")
        .master("local[*]")
        .config("spark.cores.max", "4")
        .config("spark.driver.memory", "30g")
        .enableHiveSupport()
        .config(
            "spark.sql.warehouse.dir",
            "/home/sharnqvi/VVVNewDataModel/ScienceArchives/vvx_etl/vvx-dagster/src/spark-warehouse",
        )
        .config(
            "javax.jdo.option.ConnectionURL",
            f"jdbc:derby:;databaseName={metastore_location};create=true",
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
