import re
from pyspark.sql import DataFrame, SparkSession

""" Save dataframe as bucketed Spark table"""


def _sanitize_identifier(identifier: str) -> str:
    """Prevent SQL injection by ensuring identifier does not contain dangerous chars"""
    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", identifier):
        return identifier
    else:
        raise ValueError(f"Invalid SQL identifier: {identifier}")


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
    """ """"""

    key = _sanitize_identifier(key)
    table_name = _sanitize_identifier(table_name)
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
