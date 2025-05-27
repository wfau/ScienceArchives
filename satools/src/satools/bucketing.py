from satools.utils import sanitise_identifier, check_table_is_in_catalog
from satools.errors import TableNotInCatalogError
from pyspark.sql import DataFrame, SparkSession

""" Save dataframe as bucketed Spark table"""


def bucket_save(
    df: DataFrame, buckets: int, key: str, table_name: str, spark: SparkSession
) -> None:
    """Save table to Spark warehouse, bucketed by column 'key' into 'buckets' buckets.

    Args:
        df (DataFrame): Source data.
        buckets (int): Number of desired buckets.
        key (str): Column to make buckets on.
        table_name (str): Name of table in Spark warehouse.
        spark (SparkSession): Spark instance.

    Raises:
        ValueError: if number of buckets is not a positive integer.
    """

    if spark.conf.get("spark.sql.catalogImplementation") != "hive":
        raise ValueError("Spark catalog implementation must be 'hive'")

    key = sanitise_identifier(key)
    table_name = sanitise_identifier(table_name)
    if not isinstance(buckets, int) and not buckets > 0:
        raise ValueError("Buckets must be integer > 0")

    df = df.repartition(buckets, key)
    df.createOrReplaceTempView("tmp_view")
    spark.sql(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name}
        USING PARQUET
        CLUSTERED BY ({key}) INTO {buckets} BUCKETS
        AS SELECT * FROM tmp_view
    """
    )

    # (
    #     df.write.format("parquet")
    #     .bucketBy(buckets, key)
    #     .sortBy(key)
    #     .mode("overwrite")
    #     .saveAsTable(table_name)
    # )

    check_table_is_in_catalog(table_name=table_name, spark=spark)
