from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import *
from vvx_etl import bucketing, array_columns
from vvx_etl.spark_singleton import SparkSingleton
from vvx_etl.errors import *
from vvx_etl.validate_source_detection_etl import *
from vvx_etl.bucketing import bucket_save
from vvx_etl.utils import (
    cast_df_using_schema,
    get_bucketing_data,
)
import shutil
from pathlib import Path
import toml
import logging
from datetime import datetime
import os
from vvx_etl.schema import schema_joined_source_detection

logger = logging.getLogger(__name__)


def extract(
    spark: SparkSession,
    source_data_path: str,
    detection_data_path: str,
    detection_array_cols: list[str],
):

    source = spark.read.parquet(source_data_path)
    detection = spark.read.parquet(detection_data_path).select(
        "sourceID", "filterID", *detection_array_cols
    )

    return source, detection


def transform(
    source_df: DataFrame,
    detection_df: DataFrame,
    cols_to_transform: list[str],
    schema: StructType,
    spark: SparkSession,
):
    """Make Detection array-valued, and join with source."""

    detection_arrayvals_df = array_columns.make_array_cols(
        detection_df,
        key="sourceID",
        filter_col="filterID",
        order_by="sourceID",
        cols_to_transform=cols_to_transform,
    )

    bucket_save(
        df=detection_arrayvals_df,
        buckets=8,
        key="sourceID",
        table_name="detection_arrays_bucketed",
        spark=spark,
    )

    bucket_save(
        df=source_df,
        buckets=8,
        key="sourceID",
        table_name="source_bucketed",
        spark=spark,
    )

    detection_bucketing = get_bucketing_data(
        spark=spark, table_name="detection_arrays_bucketed"
    )
    source_bucketing = get_bucketing_data(spark=spark, table_name="source_bucketed")

    if detection_bucketing != source_bucketing:
        raise BucketingError(
            f"❌ Dataframes are not bucketed the same way - found: \n *Source* \n {source_bucketing} \n Detection: \n {detection_bucketing}"
        )
    elif not detection_bucketing or len(detection_bucketing) == 0:
        raise BucketingError("❌ No bucketing found for detection")
    elif not source_bucketing or len(source_bucketing) == 0:
        raise BucketingError("❌ No bucketing found for source")

    joined = spark.table("source_bucketed").join(
        spark.table("detection_arrays_bucketed"), on="sourceID"
    )

    joined = cast_df_using_schema(df=joined, schema=schema_joined_source_detection)

    return joined


def load(
    joined_df: DataFrame, buckets: int, joined_table_name: str, spark: SparkSession
):
    """Load to Spark warehouse as bucketed parquet."""

    spark.sql("CREATE DATABASE IF NOT EXISTS default")

    bucketing.bucket_save(
        joined_df,
        buckets=buckets,
        key="sourceID",
        table_name=joined_table_name,
        spark=spark,
    )


def pipeline():

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"etl_log_{timestamp}.log"
    os.makedirs("logs", exist_ok=True)
    log_path = os.path.join("logs", log_filename)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.FileHandler(log_path, mode="a"), logging.StreamHandler()],
    )

    configs = toml.load("etl_config.toml")

    logging.info(f"SETUP INFO: \n ** Configs ** \n {configs}. \n")

    warehouse_dir = Path(configs["spark_warehouse"]["path"])
    if warehouse_dir.exists() and configs["spark_warehouse"]["overwrite"]:
        shutil.rmtree(warehouse_dir, ignore_errors=True)
        shutil.rmtree(warehouse_dir.parent / "metastore_db", ignore_errors=True)

    columns_to_array_value = configs["transform"]["columns_to_array_value"]
    joined_table_name = configs["table_names"]["source_detection"]

    with SparkSingleton(warehouse_dir=warehouse_dir) as spark:
        logger.info("Extracting data")
        source, detection = extract(
            spark,
            source_data_path=configs["parquet_paths"]["source"],
            detection_data_path=configs["parquet_paths"]["detection"],
            detection_array_cols=columns_to_array_value,
        )
        logger.info("Data extracted")

        logger.info("Transforming data")
        joined = transform(
            source_df=source,
            detection_df=detection,
            cols_to_transform=columns_to_array_value,
            schema=schema_joined_source_detection,
            spark=spark,
        )
        logger.info("Transformation complete")

        logger.info("Loading data")
        load(
            joined_df=joined,
            buckets=configs["partitioning"]["n_buckets"],
            joined_table_name=joined_table_name,
            spark=spark,
        )
        logger.info("Data loaded")

        logger.info("Validating final data")
        joined_read_from_table = spark.table(joined_table_name)

        try:
            validate_consistent_nrows(detection=detection, final=joined_read_from_table)
            logger.info(
                "✅ Number of unique key entries match between Detection and the joined table"
            )
        except InconsistentRowCountError as e:
            logger.error(f"❌ Validation failed: {e}")

        try:
            validate_schema(
                expected=schema_joined_source_detection,
                observed=joined_read_from_table.schema,
            )
            logger.info("✅ Schema matches expectation")
        except InconsistentSchemaError as e:
            logger.error(f"❌ Validation failed: {e}")

        try:
            validate_bucketing(
                table_name=joined_table_name,
                buckets=configs["partitioning"]["n_buckets"],
                key="sourceID",
                spark=spark,
            )
            logger.info("✅ Bucketing matches expectations")
        except BucketingError as e:
            logger.error(f"❌ Validation failed: {e}")


if __name__ == "__main__":
    pipeline()
