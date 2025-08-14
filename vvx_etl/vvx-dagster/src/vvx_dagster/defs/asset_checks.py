from dagster import AssetCheckResult, asset_check, AssetCheckExecutionContext
import dagster as dg
from pathlib import Path
from typing import List
from .configs import CONFIG
from ..transformations.validation import (
    validate_bucketing,
    validate_consistent_nrows,
    validate_schema,
)
from ..transformations.schema import schema_joined_source_detection
from .assets import (
    joined_qppv,
    vvv_src5,
    detection_array_valued_bucketed,
    source_detection_joined,
)
from .resources import SparkResource
import glob
import os


def check_parquets_exist(table_name: str) -> AssetCheckResult:
    expected_path = Path(CONFIG.download_dir).joinpath(table_name)
    all_parquets = glob.glob(
        os.path.join(CONFIG.download_dir, "**", "*.parquet"), recursive=True
    )
    if expected_path.exists() and any(list(all_parquets)):
        return AssetCheckResult(passed=True)
    else:
        return AssetCheckResult(
            passed=False, description=f"No Parquet files found in {expected_path}"
        )


def check_table_exists(spark: SparkResource, table_name: str) -> AssetCheckResult:
    spark_session = spark.get_session()
    if spark_session.catalog.tableExists(CONFIG.spark_db, table_name):
        return AssetCheckResult(passed=True)
    else:
        return AssetCheckResult(passed=False)


@asset_check(asset=joined_qppv, blocking=True)
def check_joined_qppv_files_exist() -> AssetCheckResult:
    return check_parquets_exist("JoinedQPPV")


@asset_check(asset=joined_qppv, blocking=True)
def check_joined_qppv_table_exists(spark: SparkResource) -> AssetCheckResult:
    return check_table_exists(spark, "joined_qppv")


@asset_check(asset=vvv_src5, blocking=True)
def check_joined_vvv_src5_table_exists(spark: SparkResource) -> AssetCheckResult:
    return check_table_exists(spark, "vvv_src5")


# Check: vvv_src5 files exist
@asset_check(asset=vvv_src5, blocking=True)
def check_vvv_src5_files_exist() -> AssetCheckResult:
    return check_parquets_exist("vvvSrc5")


# Check: detection_array_valued_bucketed is correctly bucketed
@asset_check(
    asset=detection_array_valued_bucketed,
    blocking=True,
    description="Ensure Detection is bucketed correctly",
)
def detection_correctly_bucketed(
    spark: SparkResource,
) -> AssetCheckResult:
    spark_session = spark.get_session()
    return AssetCheckResult(
        passed=validate_bucketing(
            "detection_arrays_bucketed",
            buckets=CONFIG.n_buckets,
            key="sourceID",
            spark=spark_session,
        )
    )


# Check: source_bucketed is correctly bucketed
@asset_check(
    asset=vvv_src5,
    blocking=True,
    description="Ensure Source is bucketed correctly",
)
def source_correctly_bucketed(
    spark: SparkResource,
) -> AssetCheckResult:
    spark_session = spark.get_session()
    return AssetCheckResult(
        passed=validate_bucketing(
            "vvv_src5",
            buckets=CONFIG.n_buckets,
            key="sourceID",
            spark=spark_session,
        )
    )


# Check: source_detection_joined is correctly bucketed
@asset_check(
    asset=source_detection_joined,
    name="correct_bucketing",
    blocking=True,
    description="Ensure joined Source-Detection is bucketed correctly",
)
def source_detection_joined_correctly_bucketed(
    spark: SparkResource,
) -> AssetCheckResult:
    spark_session = spark.get_session()
    return AssetCheckResult(
        passed=validate_bucketing(
            "source_detection_joined",
            buckets=CONFIG.n_buckets,
            key="sourceID",
            spark=spark_session,
        )
    )


# Check: row count consistency
@asset_check(
    asset=source_detection_joined,
    name="count_rows",
    blocking=True,
    description="Ensure Detection and the joined table have the same number of rows",
)
def detection_and_joined_consistent_rows(
    spark: SparkResource,
) -> AssetCheckResult:
    spark_session = spark.get_session()
    detection_nrows = spark_session.sql(
        "SELECT COUNT(*) FROM detection_arrays_bucketed"
    ).collect()[0][0]
    joined_nrows = spark_session.sql(
        "SELECT COUNT(*) FROM source_detection_joined"
    ).collect()[0][0]
    return AssetCheckResult(passed=detection_nrows == joined_nrows)


# Check: schema match
@asset_check(
    asset=source_detection_joined,
    name="schema_match",
    blocking=True,
    description="Check that joined table matches expected schema",
)
def source_detection_joined_matches_schema(
    spark: SparkResource,
) -> AssetCheckResult:
    spark_session = spark.get_session()
    expected_schema = schema_joined_source_detection
    actual_schema = spark_session.table("source_detection_joined").schema
    return AssetCheckResult(
        passed=validate_schema(expected=expected_schema, observed=actual_schema)
    )
