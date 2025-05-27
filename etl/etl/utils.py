from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col
from pyspark.sql.types import StructType
from etl.errors import TableNotInCatalogError
import os
import re


def check_table_is_in_catalog(table_name: str, spark: SparkSession) -> None:
    if not table_name in [t.name for t in spark.catalog.listTables()]:
        raise TableNotInCatalogError(
            f"Table {table_name} not found in Spark catalog. Found tables: {spark.catalog.listTables()}. Database: {spark.catalog.currentDatabase()}"
        )


def get_table_location(spark: SparkSession, table_name: str) -> str:
    """Get the physical location of a Spark SQL table."""
    desc = spark.sql(f"DESCRIBE TABLE EXTENDED {table_name}").collect()
    for row in desc:
        if row.col_name.strip().lower() == "location":
            return row.data_type
    raise ValueError(f"Could not find location for table {table_name}")


def count_parquet_files(spark: SparkSession, table_name: str) -> int:
    """Count number of parquet files that a table is partitioned into."""
    table_path = get_table_location(spark, table_name)
    if table_path.startswith("file:"):
        table_path = table_path.replace("file:", "", 1)
    try:
        return sum(1 for f in os.listdir(table_path) if f.endswith(".parquet"))
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Directory {table_path} not found. Is the table created?"
        )


def get_bucketing_data(table_name: str, spark: SparkSession) -> dict:
    """Get bucketing information from Spark SQL table metadata."""
    bucketing_data = {}
    desc = spark.sql(f"DESCRIBE TABLE EXTENDED {table_name}").collect()

    for row in desc:
        if "Num Buckets" in row.col_name:
            bucketing_data["n_buckets"] = int(row.data_type.strip())
        elif "Bucket Columns" in row.col_name:
            # data_type might look like: `[sourceID]`
            bucketing_data["bucket_col"] = row.data_type.strip("`[]").split(", ")

    return bucketing_data


def is_correctly_bucketed(
    table_name: str, spark: SparkSession, buckets: int, key: str
) -> bool:
    """Check whether a table is bucketed correctly by bucket count and column."""
    info = get_bucketing_data(table_name, spark)

    if info.get("n_buckets") != buckets:
        raise ValueError(
            f"Expected {buckets} buckets, but found {info.get('n_buckets')}"
        )

    if [key] != info.get("bucket_col", []):
        raise ValueError(
            f"Expected bucket column {key}, but found {info.get('bucket_col')}"
        )

    return True


def sanitise_identifier(identifier: str) -> str:
    """Prevent SQL injection by ensuring identifier does not contain dangerous chars"""
    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", identifier):
        return identifier
    else:
        raise ValueError(f"Invalid SQL identifier: {identifier}")


def cast_df_using_schema(df: DataFrame, schema: StructType):
    return df.select(
        [
            col(field.name).cast(field.dataType).alias(field.name)
            for field in schema.fields
        ]
    )
