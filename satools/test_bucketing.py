import shutil
import os
import pytest
import random
from bucketing import bucket_save
from pyspark.sql import SparkSession
from pyspark.sql.functions import monotonically_increasing_id


@pytest.fixture(scope="module")
def spark():
    spark = (
        SparkSession.builder.appName("BucketingTest")
        .master("local[2]")
        .enableHiveSupport()
        .getOrCreate()
    )
    yield spark
    spark.stop()


def make_table(n_rows, spark):
    columns = ["index", "col1", "col2", "col3"]
    data = [
        (
            random.choice(["A", "B", "C", "D"]),
            random.randint(1, 100),
            random.uniform(1.0, 100.0),
        )
        for _ in range(n_rows)
    ]
    df = spark.createDataFrame(data, schema=columns[1:])
    df = df.withColumn("index", monotonically_increasing_id())
    return df


def is_correctly_bucketed(table_name, spark, buckets, key):
    buckets_df = get_bucketing_data(table_name, spark)
    return buckets_df["n_buckets"] == buckets and buckets_df["bucket_col"] == key


def count_parquet_files(table_name):
    table_path = os.path.join("spark-warehouse", table_name)
    return sum(1 for f in os.listdir(table_path) if f.endswith(".parquet"))


def get_bucketing_data(table_name, spark):
    bucketing_data = {}
    desc = spark.sql(f"DESCRIBE TABLE EXTENDED {table_name}").collect()

    for row in desc:
        if "Num Buckets" in row.col_name:
            bucketing_data["n_buckets"] = row.data_type
        elif "Bucket Columns" in row.col_name:
            bucketing_data["bucket_col"] = row.data_type.strip("`[]")

    return bucketing_data


@pytest.mark.parametrize("n_rows,buckets,key", [(1000, 2, "index")])
def test_bucket_save(spark, n_rows, buckets, key):
    table_name = "test_bucketed_table"

    try:
        spark.sql(f"DROP TABLE IF EXISTS {table_name}")
    except Exception:
        pass
    shutil.rmtree(f"spark-warehouse/{table_name}", ignore_errors=True)

    df = make_table(n_rows, spark)
    bucket_save(df, buckets=buckets, key=key, table_name=table_name, spark=spark)

    assert is_correctly_bucketed(
        table_name, spark, str(buckets), key
    ), "Table is not correctly bucketed"

    n_files = count_parquet_files(table_name)
    assert n_files == buckets, f"Expected {buckets} parquet files, got {n_files}"
