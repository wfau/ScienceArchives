import dagster as dg
from dagster import AssetCheckResult, asset_check, AssetCheckExecutionContext
from pathlib import Path
import os
import glob

from .configs import CONFIG
from ..transformations.schema import schema_joined_source_detection
from ..transformations.extract import get_mods
from .resources import SparkResource
from .assets import (
    joined_qppv,
    vvv_src5,
    detection_array_valued,
    source_detection_joined,
)

from ..transformations.validation import validate_schema


def check_parquets_exist(folder: str) -> AssetCheckResult:
    """Check that there is at least one .parquet file in the specified folder."""
    expected_path = Path(CONFIG.download_dir).joinpath(folder)
    parquet_files = glob.glob(str(expected_path / "**/*.parquet"), recursive=True)

    if expected_path.exists() and parquet_files:
        return AssetCheckResult(passed=True)
    else:
        return AssetCheckResult(
            passed=False,
            description=f"No parquet files found in {expected_path}",
        )


@asset_check(asset=joined_qppv, blocking=True)
def check_joined_qppv_files_exist() -> AssetCheckResult:
    return check_parquets_exist("JoinedQPPV")


@asset_check(asset=vvv_src5, blocking=True)
def check_vvv_src5_files_exist() -> AssetCheckResult:
    return check_parquets_exist("vvvSrc5")


@asset_check(asset=detection_array_valued, blocking=True)
def check_detection_array_files_exist() -> AssetCheckResult:
    return check_parquets_exist("DetectionArrays")


@asset_check(asset=source_detection_joined, blocking=True)
def check_source_detection_joined_files_exist() -> AssetCheckResult:
    return check_parquets_exist("source_detection_joined")


# Check: source_detection_joined matches expected schema
@asset_check(
    asset=source_detection_joined,
    name="schema_match",
    blocking=True,
    description="Check that a sampled mod of the joined table matches the expected schema",
)
def check_source_detection_schema(spark: SparkResource) -> AssetCheckResult:
    spark_session = spark.get_session()

    # Sample a mod from the written files
    joined_path = Path(CONFIG.download_dir).joinpath("source_detection_joined")
    mod_folders = [f for f in joined_path.glob("*") if f.is_dir()]

    if not mod_folders:
        return AssetCheckResult(
            passed=False, description="No mod folders found in joined output."
        )

    sample_path = str(mod_folders[0] / "*.parquet")
    df = spark_session.read.parquet(sample_path)
    observed_schema = df.schema

    return AssetCheckResult(
        passed=validate_schema(
            expected=schema_joined_source_detection, observed=observed_schema
        )
    )


@asset_check(
    asset=source_detection_joined,
    name="row_consistency",
    blocking=True,
    description="Check that source_detection_joined and detection_array have consistent row counts for a sample mod",
)
def check_row_consistency(spark: SparkResource) -> AssetCheckResult:
    spark_session = spark.get_session()

    base_dir = Path(CONFIG.download_dir)
    detection_mods = sorted(
        [p for p in (base_dir / "DetectionArrays").glob("*") if p.is_dir()]
    )
    joined_mods = sorted(
        [p for p in (base_dir / "source_detection_joined").glob("*") if p.is_dir()]
    )

    # Choose a mod that exists in both
    common = set(p.name for p in detection_mods).intersection(
        p.name for p in joined_mods
    )
    if not common:
        return AssetCheckResult(
            passed=False, description="No common mod folders found."
        )

    sample_mod = list(common)[0]

    df_detection = spark_session.read.parquet(
        str(base_dir / "DetectionArrays" / sample_mod)
    )
    df_joined = spark_session.read.parquet(
        str(base_dir / "source_detection_joined" / sample_mod)
    )

    passed = df_detection.count() == df_joined.count()

    return AssetCheckResult(
        passed=passed,
        description=f"Rows: detection={df_detection.count()}, joined={df_joined.count()}",
    )
