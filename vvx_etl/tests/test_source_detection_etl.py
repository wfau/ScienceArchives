import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import col, udf
from etl.spark_singleton import SparkSingleton
from etl.source_detection_etl import extract, transform, load
from etl.schema import schema_joined_source_detection
from etl.utils import check_schema_alignment
import toml
import os
import shutil
import math
from spark_fixture import spark_fixture

DETECTION_ARRAY_COLS = toml.load("tests/test_etl_config.toml")["transform"][
    "columns_to_array_value"
]
SOURCE_PATH = "example_data/source"
DETECTION_PATH = "example_data/detection"
VARIABILITY_PATH = "example_data/variability"


@pytest.fixture(scope="module")
def etl_output_table():
    """Provide the name of the test output table (shared across tests)."""
    return "test_joined_table"


@pytest.fixture(scope="module", autouse=True)
def run_etl_once(spark_fixture, etl_output_table, request):
    """Run the ETL pipeline once per test session, and clean up after."""
    source_path = SOURCE_PATH
    detection_path = DETECTION_PATH
    detection_array_cols = DETECTION_ARRAY_COLS

    # Run pipeline
    source_df, detection_df = extract(
        spark=spark_fixture,
        source_data_path=source_path,
        detection_data_path=detection_path,
        detection_array_cols=detection_array_cols,
    )

    joined_df = transform(
        source_df=source_df,
        detection_df=detection_df,
        cols_to_transform=detection_array_cols,
        schema=schema_joined_source_detection,
        spark=spark_fixture,
    )

    load(
        joined_df=joined_df,
        buckets=8,
        joined_table_name=etl_output_table,
        spark=spark_fixture,
    )

    spark_fixture.catalog.clearCache()

    def teardown():
        spark_fixture.sql(f"DROP TABLE IF EXISTS {etl_output_table}")
        spark_fixture.catalog.clearCache()

        warehouse_path = spark_fixture.conf.get("spark.sql.warehouse.dir")
        table_dir = os.path.join(warehouse_path, etl_output_table)
        if os.path.exists(table_dir):
            shutil.rmtree(table_dir, ignore_errors=True)

    request.addfinalizer(teardown)


# --- Test Cases --- #


def test_table_exists(spark_fixture, etl_output_table):
    tables = spark_fixture.catalog.listTables()
    assert any(
        t.name == etl_output_table for t in tables
    ), f"Table {etl_output_table} does not exist"


def test_schema_matches_expected(spark_fixture, etl_output_table):
    df = spark_fixture.table(etl_output_table)
    actual_schema = df.schema
    expected_schema = schema_joined_source_detection
    check_schema_alignment(expected=expected_schema, observed=actual_schema)


def test_joined_table_is_bucketed(spark_fixture, etl_output_table):
    desc = spark_fixture.sql(f"DESCRIBE FORMATTED {etl_output_table}").collect()
    bucket_info = [
        row for row in desc if "Num Buckets" in row[0] or "Bucket Columns" in row[0]
    ]

    assert any("Num Buckets" in row[0] for row in bucket_info), "Table is not bucketed"
    assert any(
        "sourceID" in row[1] for row in bucket_info
    ), "Table is not bucketed by sourceID"


def test_source_detection_join_no_shuffle(spark_fixture):

    joined = spark_fixture.table("source_bucketed").join(
        spark_fixture.table("detection_arrays_bucketed"), on="sourceID"
    )

    plan = joined._jdf.queryExecution().executedPlan().toString()
    assert "Exchange" not in plan, f"Join is causing a shuffle."


@udf(IntegerType())
def n_elems(arr):
    if arr is None:
        return 0
    return len(
        [elem for elem in arr if elem is not None and not math.isnan(elem) and elem > 0]
    )


def test_correct_number_of_obs(spark_fixture, etl_output_table):

    variability = spark_fixture.read.parquet(VARIABILITY_PATH).select(
        "sourceID", "ksnGoodObs", "ksnFlaggedObs", "ksBestAper"
    )

    res = (
        spark_fixture.table(etl_output_table)
        .select("sourceID", "ksEpochAperMag1")
        .join(variability, on="sourceID", how="inner")
        .withColumn("observed_n_obs", n_elems("ksEpochAperMag1"))
        .withColumn("expected_n_obs", col("ksnGoodObs") + col("ksnFlaggedObs"))
        .filter(col("ksBestAper") == 1)
    )

    assert res.filter(col("expected_n_obs") != col("observed_n_obs")).count() == 0
