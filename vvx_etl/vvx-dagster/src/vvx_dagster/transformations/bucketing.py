from .utils import sanitise_identifier, check_table_is_in_catalog
from .errors import TableNotInCatalogError
from pyspark.sql import DataFrame, SparkSession
from pathlib import Path
import shutil
from urllib.parse import urlparse

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

    key = sanitise_identifier(key)
    table_name = sanitise_identifier(table_name)
    if not isinstance(buckets, int) and not buckets > 0:
        raise ValueError("Buckets must be integer > 0")

    df = df.repartition(buckets, key)

    warehouse_dir = urlparse(spark.conf.get("spark.sql.warehouse.dir")).path
    table_path = Path(warehouse_dir).joinpath(table_name)

    if table_path.exists() and table_path.is_dir():
        shutil.rmtree(table_path)
        print(f"Removing location {table_path}")

    df.createOrReplaceTempView("tmp_view")

    if not spark.catalog.tableExists(table_name):
        spark.sql(
            f"""
            CREATE TABLE {table_name}
            USING PARQUET
            CLUSTERED BY ({key}) INTO {buckets} BUCKETS
            AS SELECT * FROM tmp_view
            """
        )
    else:
        spark.sql(f"INSERT OVERWRITE TABLE {table_name} SELECT * FROM tmp_view")

    check_table_is_in_catalog(table_name=table_name, spark=spark)
