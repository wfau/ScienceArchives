import pytest
import time
import math
from pyspark.sql.functions import col, udf
from pyspark.sql.types import IntegerType, FloatType, ArrayType
from satools.bucketing import bucket_save
from satools.utils import is_correctly_bucketed
from satools.array_columns import make_array_cols
from pyspark.sql import SparkSession
from pathlib import Path
import os, shutil


EXAMPLE_DATA_PATH = Path("tests/example_data").resolve()


@pytest.fixture(scope="session")
def spark_fixture(tmp_path_factory):

    warehouse_dir = tmp_path_factory.mktemp("spark_warehouse")
    WAREHOUSE_PATH = str(warehouse_dir)

    spark = (
        SparkSession.builder.appName("PySpark integration test")
        .master("local[2]")
        .config("spark.sql.warehouse.dir", WAREHOUSE_PATH)
        .config("spark.sql.warehouse.dir", str(warehouse_dir))
        .config("spark.driver.memory", "1g")
        .config("spark.executor.memory", "1g")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )
    yield spark
    spark.stop()


def make_bucketed_fixture(path, table_name):
    @pytest.fixture
    def _fixture(spark_fixture):
        df = spark_fixture.read.parquet(str(path))
        bucket_save(
            df, buckets=10, key="sourceID", table_name=table_name, spark=spark_fixture
        )
        return df

    return _fixture


source_data = make_bucketed_fixture(
    EXAMPLE_DATA_PATH.joinpath("source"), "source_bucketed"
)
detection_data = make_bucketed_fixture(
    EXAMPLE_DATA_PATH.joinpath("detection"), "detection_bucketed"
)
variability_data = make_bucketed_fixture(
    EXAMPLE_DATA_PATH.joinpath("variability"), "variability_bucketed"
)


def test_source_table_created(source_data):
    assert "source_bucketed" in [
        t.name for t in source_data.sparkSession.catalog.listTables()
    ]


def test_detection_table_created(detection_data):
    assert "detection_bucketed" in [
        t.name for t in detection_data.sparkSession.catalog.listTables()
    ]


def test_variability_table_created(variability_data):
    assert "variability_bucketed" in [
        t.name for t in variability_data.sparkSession.catalog.listTables()
    ]


def test_source_bucketed_correctly(spark_fixture):
    assert is_correctly_bucketed(
        "source_bucketed", spark_fixture, buckets=10, key="sourceID"
    )


def test_detections_bucketed_correctly(spark_fixture):
    assert is_correctly_bucketed(
        "detection_bucketed", spark_fixture, buckets=10, key="sourceID"
    )


def test_variability_bucketed_correctly(spark_fixture):
    assert is_correctly_bucketed(
        "variability_bucketed", spark_fixture, buckets=10, key="sourceID"
    )


@pytest.fixture
def array_transformed_detection(spark_fixture):
    spark_fixture.sql("DROP TABLE IF EXISTS detection_arraycols")
    spark_fixture.catalog.clearCache()
    time.sleep(0.5)

    df = spark_fixture.table("detection_bucketed")
    transformed = make_array_cols(
        df, key="sourceID", filter_col="filterID", order_by="sourceID"
    )

    bucket_save(
        transformed,
        buckets=10,
        key="sourceID",
        table_name="detection_arraycols",
        spark=spark_fixture,
    )
    return spark_fixture.table("detection_arraycols")


def test_correct_cols_in_array_transformed_detection(array_transformed_detection):
    assert "ksEpochAperMag1" in array_transformed_detection.columns
    field = array_transformed_detection.schema["ksEpochAperMag1"]
    assert isinstance(field.dataType, ArrayType)
    assert isinstance(field.dataType.elementType, FloatType)


@pytest.fixture
def source_detection_joined(spark_fixture, array_transformed_detection):
    spark_fixture.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)
    source_df = spark_fixture.table("source_bucketed")
    detection_df = spark_fixture.table("detection_arraycols")

    source_detection_df = source_df.join(detection_df, on="sourceID", how="inner")
    bucket_save(
        source_detection_df,
        buckets=10,
        key="sourceID",
        table_name="source_detection",
        spark=spark_fixture,
    )
    return spark_fixture.table("source_detection")


def test_source_detection_bucketed(spark_fixture, source_detection_joined):
    assert is_correctly_bucketed(
        "source_detection", spark_fixture, buckets=10, key="sourceID"
    )


def test_left_source_detection_joined_correctness(source_detection_joined):
    assert source_detection_joined.count() > 0
    no_match = source_detection_joined.filter(
        col("source_detection.sourceID").isNull()
    ).count()
    assert no_match == 0


def test_physical_plan_for_no_shuffle(source_detection_joined):
    plan = source_detection_joined._jdf.queryExecution().toString()
    shuffle_keywords = ["Exchange", "ShuffledHashJoin"]
    assert not any(k in plan for k in shuffle_keywords), f"Shuffle detected:\n{plan}"


@udf(IntegerType())
def n_elems(arr):
    if arr is None:
        return 0
    return len(
        [elem for elem in arr if elem is not None and not math.isnan(elem) and elem > 0]
    )


def test_correct_number_of_obs(source_detection_joined, spark_fixture):
    true_obs = spark_fixture.sql(
        """
        SELECT sourceID, ksnGoodObs, ksnFlaggedObs, ksBestAper 
        FROM variability_bucketed
    """
    )

    res = (
        source_detection_joined.select(
            col("source_detection.sourceID"), col("source_detection.ksEpochAperMag1")
        )
        .join(true_obs, on="sourceID", how="inner")
        .withColumn("observed_n_obs", n_elems("ksEpochAperMag1"))
        .withColumn("expected_n_obs", col("ksnGoodObs") + col("ksnFlaggedObs"))
        .filter(col("ksBestAper") == 1)
    )

    assert res.filter(col("expected_n_obs") != col("observed_n_obs")).count() == 0
