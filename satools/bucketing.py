import re
from pyspark.sql import DataFrame, SparkSession


def _sanitize_identifier(identifier: str):
    """Prevent SQL injection by ensuring identifier does not contain dangerous chars"""
    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", identifier):
        return identifier
    else:
        raise ValueError(f"Invalid SQL identifier: {identifier}")


def bucket_save(
    df: DataFrame, buckets: int, key: str, table_name: str, spark: SparkSession
):

    key = _sanitize_identifier(key)
    table_name = _sanitize_identifier(table_name)
    if not isinstance(int, buckets) and not buckets > 0:
        raise ValueError("Buckets must be integer > 0")

    df = df.repartition(buckets, key)
    df.createOrReplaceTempView("tmp_view")
    spark.sql(
        f"""
        CREATE TABLE {table_name}
        USING PARQUET
        CLUSTERED BY ({key}) INTO {buckets} BUCKETS
        AS SELECT * FROM tmp_view
    """
    )
