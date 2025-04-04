import pytest
from pyspark.testing import assertDataFrameEqual
from pyspark.sql import SparkSession
from array_columns import transform_passbands, pivot_aggregate_col, merge_all, make_array_cols


@pytest.fixture
def spark_context():
    return SparkSession.builder.getOrCreate()


@pytest.fixture
def sample_data(spark_context):
    return spark_context.createDataFrame(
    [
        (1, 1, 1.234, 2.567),
        (1, 2, 3.234, 4.567),
        (1, 3, 5.234, 6.567),
        (1, 4, 7.234, 8.567),
        (1, 5, 9.234, 10.567),
        (2, 1, 1.234, 2.567),
        (2, 2, 3.234, 4.567),
        (2, 3, 5.234, 6.567),
        (2, 4, 7.234, 8.567),
        (2, 5, 9.234, 10.567),
        (3, 1, 1.234, 2.567),
        (3, 2, 3.234, 4.567),
        (3, 3, 5.234, 6.567),
        (3, 4, 7.234, 8.567),
        (3, 5, 9.234, 10.567)],
    ["sourceID", "filterID", "mjd", "aperMag1"])


def test_transform_passbands(sample_data, spark_context):

    actual = transform_passbands(sample_data, filter_col="filterID", new_col_name="passband")
    expected = spark_context.createDataFrame(
        [
        (1, 1, 1.234, 2.567, "Z"),
        (1, 2, 3.234, 4.567, "Y"),
        (1, 3, 5.234, 6.567, "J"),
        (1, 4, 7.234, 8.567, "H"),
        (1, 5, 9.234, 10.567, "K"),
        (2, 1, 1.234, 2.567, "Z"),
        (2, 2, 3.234, 4.567, "Y"),
        (2, 3, 5.234, 6.567, "J"),
        (2, 4, 7.234, 8.567, "H"),
        (2, 5, 9.234, 10.567, "K"),
        (3, 1, 1.234, 2.567, "Z"),
        (3, 2, 3.234, 4.567, "Y"),
        (3, 3, 5.234, 6.567, "J"),
        (3, 4, 7.234, 8.567, "H"),
        (3, 5, 9.234, 10.567, "K")],
    ["sourceID", "filterID", "mjd", "aperMag1", "passband"])

    assertDataFrameEqual(actual, expected)

def test_pivot_aggregate_columns(sample_data, spark_context):
    df = transform_passbands(sample_data, filter_col="filterID", new_col_name="passband")
    grouped = df.groupBy("sourceID")
    actual = pivot_aggregate_col(grouped, col_name="mjd", pivot_on="passband")
    expected = spark_context.createDataFrame(
    [
        (1, [7.234], [5.234], [9.234], [3.234], [1.234]),       
        (2, [7.234], [5.234], [9.234], [3.234], [1.234]),
        (3, [7.234], [5.234], [9.234], [3.234], [1.234])],
    ["sourceID", "H_mjd", "J_mjd", "K_mjd", "Y_mjd", "Z_mjd"]
)
    
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
    [(1, [7.234], [5.234], [9.234], [3.234], [1.234], [8.567], [6.567], [10.567], [4.567], [2.567]),
     (2, [7.234], [5.234], [9.234], [3.234], [1.234], [8.567], [6.567], [10.567], [4.567], [2.567]),
     (3, [7.234], [5.234], [9.234], [3.234], [1.234], [8.567], [6.567], [10.567], [4.567], [2.567])],
     ["sourceID", "H_mjd", "J_mjd", "K_mjd", "Y_mjd", "Z_mjd", "H_aperMag1", "J_aperMag1", "K_aperMag1", "Y_aperMag1", "Z_aperMag1"])
    actual = make_array_cols(sample_data, key="sourceID", filter_col="filterID")
    assertDataFrameEqual(actual, expected)
