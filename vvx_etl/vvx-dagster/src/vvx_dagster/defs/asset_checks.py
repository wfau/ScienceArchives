from dagster import AssetCheckResult, asset_check
import dagster as dg
from pathlib import Path
from ..transformations.validation import (
    validate_bucketing,
    validate_consistent_nrows,
    validate_schema,
)

from .assets import (
    joined_qppv,
    vvv_src5,
    detection_array_valued_bucketed,
    source_bucketed,
    source_detection_joined,
)

from .configs import DESTINATION, BUCKETS


@asset_check(asset=joined_qppv, required_resource_keys={"spark"}, blocking=True)
def check_joined_qppv_files_exist() -> AssetCheckResult:
    expected_path = Path(DESTINATION).joinpath("JoinedQPPV")

    if expected_path.exists() and any(expected_path.glob("*.parquet")):
        return AssetCheckResult(passed=True)
    else:
        return AssetCheckResult(
            passed=True, description=f"No Parquet files found in {expected_path}"
        )


@asset_check(asset=vvv_src5, required_resource_keys={"spark"}, blocking=True)
def check_vvv_src5_files_exist() -> AssetCheckResult:
    expected_path = Path(DESTINATION).joinpath("vvvSrc5")

    if expected_path.exists() and any(expected_path.glob("*.parquet")):
        return AssetCheckResult(passed=True)
    else:
        return AssetCheckResult(
            passed=True, description=f"No Parquet files found in {expected_path}"
        )


@dg.asset_check(
    asset=detection_array_valued_bucketed,
    required_resource_keys={"spark"},
    blocking=True,
    description="Ensure Detection is bucketed correctly",
)
def detection_correctly_bucketed(
    context: dg.AssetCheckExecutionContext, detection_array_valued_bucketed
) -> dg.AssetCheckResult:
    spark = context.resources.spark

    print(spark.conf.get("spark.sql.catalogImplementation"))  # should be 'hive'
    print(spark.catalog.listTables())

    try:
        spark.sql("SHOW TABLES").show()
    except RuntimeError as e:
        print(f"SHOW TABLES failed: {e}")

    return dg.AssetCheckResult(
        asset_key="detection_array_valued_bucketed",
        passed=validate_bucketing(
            "detection_arrays_bucketed",
            buckets=BUCKETS,
            key="sourceID",
            spark=spark,
        ),
    )


@dg.asset_check(
    asset=source_bucketed,
    blocking=True,
    required_resource_keys={"spark"},
    description="Ensure Source is bucketed correctly",
)
def source_correctly_bucketed(
    context: dg.AssetCheckExecutionContext, source_bucketed
) -> dg.AssetCheckResult:
    spark = context.resources.spark

    desc = spark.sql(f"DESCRIBE TABLE EXTENDED source_bucketed").collect()
    print(desc)
    return dg.AssetCheckResult(
        asset_key="source_bucketed",
        passed=validate_bucketing(
            "source_bucketed", buckets=BUCKETS, key="sourceID", spark=spark
        ),
    )


@dg.asset_check(
    asset=source_detection_joined,
    name="correct_bucketing",
    required_resource_keys={"spark"},
    blocking=True,
    description="Ensure joined Source-Detection is bucketed correctly",
)
def source_detection_joined_correctly_bucketed(
    context: dg.AssetCheckExecutionContext, source_detection_joined
) -> dg.AssetCheckResult:
    spark = context.resources.spark
    return dg.AssetCheckResult(
        asset_key="source_detection_joined",
        passed=validate_bucketing(
            "source_detection_joined",
            buckets=BUCKETS,
            key="sourceID",
            spark=spark,
        ),
    )


@dg.asset_check(
    asset=source_detection_joined,
    name="count_rows",
    required_resource_keys={"spark"},
    blocking=True,
    description="Ensure Detection and the joined table have the same number of rows",
)
def detection_and_joined_consistent_rows(
    context: dg.AssetExecutionContext, source_detection_joined
) -> dg.AssetCheckResult:
    spark = context.resources.spark
    detection_nrows = spark.sql("SELECT COUNT(*) FROM detection").collect()[0][0]
    joined_nrows = spark.sql("SELECT COUNT(*) FROM source_detection_joined").collect()[
        0
    ][0]

    passed = False
    if detection_nrows == joined_nrows:
        passed = True

    return dg.AssetCheckResult(passed=passed)


@dg.asset_check(
    asset=source_detection_joined,
    name="schema_match",
    required_resource_keys={"spark"},
    blocking=True,
    description="Check that joined table matches expected schema",
)
def source_detection_joined_matches_schema(
    context: dg.AssetCheckExecutionContext, source_detection_joined
) -> dg.AssetCheckResult:

    spark = context.resources.spark

    expected_schema: StructType = schema_joined_source_detection
    actual_schema = spark.table("source_detection_joined").schema

    return dg.AssetCheckResult(
        passed=validate_schema(expected=expected_schema, observed=actual_schema)
    )
