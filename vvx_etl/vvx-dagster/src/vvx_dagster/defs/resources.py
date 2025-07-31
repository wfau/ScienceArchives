from dagster_pyspark import pyspark_resource

spark = pyspark_resource.configured(
    {
        "spark_conf": {
            "spark.master": "local[*]",
            "spark.app.name": "dagster_spark_asset",
        }
    }
)
