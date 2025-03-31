import pytest
from pyspark.testing import assertDataFrameEqual
from pyspark.sql import SparkSession
from array_columns import aggregate_by_key, merge_all, make_array_cols


@pytest.fixture
def spark_context():
    return SparkSession.builder.getOrCreate()


@pytest.fixture
def sample_data(spark_context):

    df = spark_context.createDataFrame(
        [
            (1, 0.1, 0.2, 0.3),
            (1, 0.5, 0.6, 0.7),
            (2, 0.1, 0.2, 0.3),
            (2, 0.9, 1.1, 1.2),
        ],
        ["id", "col1", "col2", "col3"]
    )

    return df


def test_aggregate_by_key(spark_context, sample_data):

    expected = spark_context.createDataFrame(
        [(1, [0.1, 0.5]),
         (2, [0.1, 0.9])],
        ["id", "col1"]
    )

    grouped = sample_data.groupBy("id")
    actual = aggregate_by_key(grouped, "col1")

    assertDataFrameEqual(actual, expected)


def test_merge_all(spark_context, sample_data):

    agg_df = spark_context.createDataFrame(
        [
            (1, [0.1, 0.2, 0.3], [0.1, 0.2, 0.3], [0.1, 0.2, 0.3]),
            (2, [0.4, 0.5, 0.6], [0.1, 0.2, 0.3], [0.1, 0.2, 0.3]),
        ],
        ["id", "col1", "col2", "col3"])

    df1 = agg_df.select("id", "col1")
    df2 = agg_df.select("id", "col2")
    df3 = agg_df.select("id", "col3")

    merged = merge_all([df1, df2, df3], "id")

    assertDataFrameEqual(merged, agg_df)


def test_make_array_cols(spark_context, sample_data):
    expected = spark_context.createDataFrame(
        [(1, [0.1, 0.5], [0.2, 0.6], [0.3, 0.7]),
         (2, [0.1, 0.9], [0.2, 1.1], [0.3, 1.2])],
        ["id", "col1", "col2", "col3"]
    )
    actual = make_array_cols(sample_data, key="id")
    assertDataFrameEqual(actual, expected)
