import shutil
import os
import pytest
import random
from satools.bucketing import bucket_save
from satools.utils import is_correctly_bucketed, count_parquet_files
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
