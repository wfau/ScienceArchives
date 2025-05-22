from pyspark.sql.functions import col, udf
from pyspark.sql.types import IntegerType
import pytest
from bucketing import bucket_save
from test_bucketing import is_correctly_bucketed
import pytest
import shutil
import os


@pytest.fixture(scope="module", autouse=True)
def cleanup_tables_and_directories(_spark_session):
    # Define the locations of the tables
    table_locations = {
        "source_bucketed": "spark-warehouse/source_bucketed",
        "detection_bucketed": "spark-warehouse/detection_bucketed",
        "variability_bucketed": "spark-warehouse/variability_bucketed",
    }

    # Drop tables if they exist
    _spark_session.sql("DROP TABLE IF EXISTS source_bucketed")
    _spark_session.sql("DROP TABLE IF EXISTS detection_bucketed")
    _spark_session.sql("DROP TABLE IF EXISTS variability_bucketed")

    # Optionally remove the directories manually if needed
    for table, location in table_locations.items():
        if os.path.exists(location):
            shutil.rmtree(location)

    # Yield control to the test functions
    yield

    # Cleanup after the last test (only once after all tests)
    _spark_session.sql("DROP TABLE IF EXISTS source_bucketed")
    _spark_session.sql("DROP TABLE IF EXISTS detection_bucketed")
    _spark_session.sql("DROP TABLE IF EXISTS variability_bucketed")

    # Optionally remove the directories after the tests
    for table, location in table_locations.items():
        if os.path.exists(location):
            shutil.rmtree(location)


def make_bucketed_fixture(path, table_name):
    @pytest.fixture
    def _fixture(_spark_session):  # Use _spark_session instead of spark
        df = _spark_session.read.parquet(path)
        bucket_save(
            df, buckets=10, key="sourceID", table_name=table_name, spark=_spark_session
        )
        return df

    return _fixture


# Create fixtures for each table
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
def join_result(_spark_session):
    query = """
    SELECT * FROM source_bucketed AS s
    LEFT JOIN detection_bucketed AS d
    ON s.sourceID = d.sourceID
    """
    result_df = _spark_session.sql(query)
    return result_df


def test_left_join_result_correctness(join_result):
    assert join_result.count() > 0
    no_match_count = join_result.filter(join_result["s.sourceID"].isNull()).count()
    assert no_match_count == 0


def test_physical_plan_for_no_shuffle(join_result):
    physical_plan = join_result._jdf.queryExecution().toString()
    shuffle_keywords = ["Exchange", "ShuffledHashJoin"]
    shuffle_detected = any(keyword in physical_plan for keyword in shuffle_keywords)
    assert not shuffle_detected, f"Shuffle detected in physical plan:\n{physical_plan}"


@udf(IntegerType())
def n_elems(arr):
    return len([elem for elem in arr if elem > 0])


def test_correct_number_of_obs(join_result):
    # need to pull in variability to get observation stats
    res = (
        join_result.select(col("s.sourceID"), col("ksnGoodObs"), col("ksnFlaggedObs"))
        .withColumn("observed_n_obs", n_elems("ksEpochAperMag1"))
        .filter(col("ksBestAper") == 1)
    )
    assert res.filter(col("expected_n_obs") != col("observed_n_obs")).count() == 0
