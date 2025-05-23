from pyspark.sql import SparkSession
import os


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
