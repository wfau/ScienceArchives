import shutil
import os
import pytest
import random
from collections import namedtuple
from etl.bucketing import bucket_save
from etl.utils import is_correctly_bucketed, count_parquet_files
from spark_fixture import spark_fixture
from pyspark.sql import SparkSession
from pyspark.sql.functions import monotonically_increasing_id


@pytest.fixture(scope="module")
def spark_fixture(tmp_path_factory):
    """Provide a Spark session with a temporary warehouse directory."""
    warehouse_dir = tmp_path_factory.mktemp("spark_warehouse")
    warehouse_path = str(warehouse_dir)

    spark = (
        SparkSession.builder.appName("TestBucketing")
        .master("local[*]")
        .config("spark.sql.warehouse.dir", warehouse_path)
        .config(
            "javax.jdo.option.ConnectionURL",
            f"jdbc:derby:{warehouse_path}/metastore_db;create=true",
        )
        .config("spark.sql.catalogImplementation", "hive")
        .enableHiveSupport()
        .getOrCreate()
    )
    yield spark
    spark.stop()


def make_table(n_rows, spark_fixture):
    columns = ["index", "col1", "col2", "col3"]
    data = [
        (
            random.choice(["A", "B", "C", "D"]),
            random.randint(1, 100),
            random.uniform(1.0, 100.0),
        )
        for _ in range(n_rows)
    ]
    df = spark_fixture.createDataFrame(data, schema=columns[1:])
    df = df.withColumn("index", monotonically_increasing_id())
    return df


def get_table_location(spark_fixture, table_name):
    result = spark_fixture.sql(f"DESCRIBE FORMATTED {table_name}").collect()
    for row in result:
        if row.col_name.strip() == "Location":
            return row.data_type.strip()
    raise RuntimeError(f"Could not find location for table {table_name}")


@pytest.mark.parametrize("n_rows,buckets,key", [(1000, 2, "index")])
def test_bucket_save(spark_fixture, n_rows, buckets, key):
    table_name = "test_bucketed_table"

    spark_fixture.sql(f"DROP TABLE IF EXISTS {table_name}")

    df = make_table(n_rows, spark_fixture)
    bucket_save(
        df, buckets=buckets, key=key, table_name=table_name, spark=spark_fixture
    )

    assert is_correctly_bucketed(table_name, spark_fixture, buckets, key)

    actual_path = get_table_location(spark_fixture, table_name)
    n_files = count_parquet_files(spark_fixture, table_name)
    assert n_files == buckets, f"Expected {buckets} parquet files, got {n_files}"
