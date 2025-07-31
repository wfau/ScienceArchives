from dagster_pyspark import pyspark_resource

spark = pyspark_resource.configured(
    {
        "spark_conf": {
            "spark.master": "local[*]",
            "spark.app.name": "dagster_spark_asset",
            "spark.cores.max": "4",
            "spark.driver.memory": "30g",
            "spark.sql.warehouse.dir": "spark-warehouse",
        }
    }
)
