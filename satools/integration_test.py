from pyspark.sql.functions import col, udf
from pyspark.sql.types import IntegerType, FloatType, ArrayType
import pytest
from bucketing import bucket_save
from test_bucketing import is_correctly_bucketed
import pytest
import shutil
import os
from array_columns import make_array_cols
import math
import time


@pytest.fixture(scope="module", autouse=True)
def cleanup_tables_and_directories(_spark_session):

    tables = [
        "source_bucketed",
        "detection_bucketed",
        "variability_bucketed",
    ]

    table_locations = {table: f"spark-warehouse/{table}" for table in tables}

    for table in tables:
        _spark_session.sql(f"DROP TABLE IF EXISTS {table}")

    for table, location in table_locations.items():
        if os.path.exists(location):
            shutil.rmtree(location)

    yield  # give control back to test session

    for table in tables:
        _spark_session.sql(f"DROP TABLE IF EXISTS {table}")

    for table, location in table_locations.items():
        if os.path.exists(location):
            shutil.rmtree(location)


def make_bucketed_fixture(path, table_name):
    @pytest.fixture
    def _fixture(_spark_session):
        df = _spark_session.read.parquet(path)
        bucket_save(
            df, buckets=10, key="sourceID", table_name=table_name, spark=_spark_session
        )
        return df

    return _fixture


source_data = make_bucketed_fixture("satools/example_data/source", "source_bucketed")
detection_data = make_bucketed_fixture(
    "satools/example_data/detection", "detection_bucketed"
)
variability_data = make_bucketed_fixture(
    "satools/example_data/variability", "variability_bucketed"
)

pytest.source_data = source_data
pytest.detection_data = detection_data
pytest.variability_data = variability_data


@pytest.mark.dependency(name="source_setup")
def test_source_table_created(source_data):
    assert "source_bucketed" in [
        t.name for t in source_data.sparkSession.catalog.listTables()
    ]


@pytest.mark.dependency(name="detection_setup")
def test_detection_table_created(detection_data):
    assert "detection_bucketed" in [
        t.name for t in detection_data.sparkSession.catalog.listTables()
    ]


@pytest.mark.dependency(name="variability_setup")
def test_variability_table_created(variability_data):
    assert "variability_bucketed" in [
        t.name for t in variability_data.sparkSession.catalog.listTables()
    ]


def test_detections_bucketed_correctly(_spark_session):
    assert is_correctly_bucketed(
        "detection_bucketed", _spark_session, buckets=10, key="sourceID"
    )


def test_source_bucketed_correctly(_spark_session):
    assert is_correctly_bucketed(
        "source_bucketed", _spark_session, buckets=10, key="sourceID"
    )


def test_variability_bucketed_correctly(_spark_session):
    assert is_correctly_bucketed(
        "variability_bucketed", _spark_session, buckets=10, key="sourceID"
    )


@pytest.fixture
def array_transformed_detection(_spark_session):
    _spark_session.sql("DROP TABLE IF EXISTS detection_arraycols")

    # Let Spark release filesystem handles
    _spark_session.catalog.clearCache()
    time.sleep(1)

    table_path = "spark-warehouse/detection_arraycols"
    if os.path.exists(table_path):
        shutil.rmtree(table_path)

    detection_df = _spark_session.table("detection_bucketed")
    array_transf_detection_df = make_array_cols(
        detection_df, key="sourceID", filter_col="filterID", order_by="sourceID"
    )

    bucket_save(
        array_transf_detection_df,
        buckets=10,
        key="sourceID",
        table_name="detection_arraycols",
        spark=_spark_session,
    )
    return _spark_session.table("detection_arraycols")


@pytest.mark.dependency(depends=["detection_setup"])
def test_correct_cols_in_array_transformed_detection(array_transformed_detection):
    assert "ksEpochAperMag1" in array_transformed_detection.columns
    assert isinstance(
        array_transformed_detection.schema["ksEpochAperMag1"].dataType, ArrayType
    ), f"{'ksEpochAperMag1'} is not an ArrayType"
    assert isinstance(
        array_transformed_detection.schema["ksEpochAperMag1"].dataType.elementType,
        FloatType,
    ), f"{'ksEpochAperMag1'} is not an array of Floats"


@pytest.fixture
def source_detection_joined(_spark_session, array_transformed_detection):
    _spark_session.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)
    query = """
    SELECT * FROM source_bucketed AS s
    INNER JOIN detection_arraycols AS d
    ON s.sourceID = d.sourceID
    """
    result_df = _spark_session.sql(query)
    return result_df


def test_source_detection_bucketed(_spark_session):
    source_desc = _spark_session.sql("DESCRIBE FORMATTED source_bucketed").collect()
    detection_desc = _spark_session.sql(
        "DESCRIBE FORMATTED detection_arraycols"
    ).collect()

    def extract_buckets(desc):
        for row in desc:
            if "Num Buckets" in row[0]:
                return int(row[1].strip())
        return None

    assert (
        extract_buckets(source_desc) == 10
    ), "source_bucketed is not bucketed with 10 buckets"
    assert (
        extract_buckets(detection_desc) == 10
    ), "detection_arraycols is not bucketed with 10 buckets"


def test_left_source_detection_joined_correctness(source_detection_joined):
    assert source_detection_joined.count() > 0
    no_match_count = source_detection_joined.filter(
        source_detection_joined["s.sourceID"].isNull()
    ).count()
    assert no_match_count == 0


def test_physical_plan_for_no_shuffle(source_detection_joined):
    physical_plan = source_detection_joined._jdf.queryExecution().toString()
    shuffle_keywords = ["Exchange", "ShuffledHashJoin"]
    shuffle_detected = any(keyword in physical_plan for keyword in shuffle_keywords)
    assert not shuffle_detected, f"Shuffle detected in physical plan:\n{physical_plan}"


@udf(IntegerType())
def n_elems(arr):
    if arr is None:
        return 0
    return len(
        [elem for elem in arr if elem is not None and not math.isnan(elem) and elem > 0]
    )


def test_correct_number_of_obs(source_detection_joined, _spark_session):
    true_obs = _spark_session.sql(
        "SELECT sourceID, ksnGoodObs, ksnFlaggedObs, ksBestAper FROM variability_bucketed"
    )

    res = (
        source_detection_joined.select(col("s.sourceID"), col("d.ksEpochAperMag1"))
        .join(true_obs, how="inner", on="sourceID")
        .withColumn("observed_n_obs", n_elems("ksEpochAperMag1"))
        .withColumn("expected_n_obs", col("ksnGoodObs") + col("ksnFlaggedObs"))
        .filter(col("variability_bucketed.ksBestAper") == 1)
    )
    assert res.filter(col("expected_n_obs") != col("observed_n_obs")).count() == 0
