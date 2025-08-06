import dagster as dg
from pathlib import Path
from ..transformations.array_columns import make_array_cols
from ..transformations.bucketing import bucket_save
from ..transformations.utils import cast_df_using_schema
from ..transformations.schema import schema_joined_source_detection

from ..transformations.extract import download_parquets
import pandas as pd
from dagster import asset, AssetExecutionContext
from pyspark.sql.types import StructType
from pyspark.sql import SparkSession

from .configs import DESTINATION, BUCKETS


@asset(required_resource_keys={"spark"})
def joined_qppv(context: AssetExecutionContext) -> None:
    source_path = "http://www-wfau.roe.ac.uk/www-data/VVVXDMP/bulkOut/JoinedQPPV/"

    download_parquets(url=source_path, output_path=DESTINATION)


@asset(required_resource_keys={"spark"})
def vvv_src5(context: AssetExecutionContext) -> None:
    source_path = "http://www-wfau.roe.ac.uk/www-data/VVVXDMP/bulkOut/vvvSrc5/"
    download_parquets(url=source_path, output_path=DESTINATION)


@dg.asset(
    deps=["joined_qppv"],
    required_resource_keys={"spark"},
)
def detection_array_valued_bucketed(context: AssetExecutionContext):
    spark = context.resources.spark

    detection_df = spark.read.parquet(DESTINATION + "/JoinedQPPV/mod0000")
    columns_to_array_value = [
        "mjd",
        "aperMag1",
        "aperMag1err",
        "aperMag2",
        "aperMag2err",
        "aperMag3",
        "aperMag3err",
        "errBits",
        "averageConf",
        "class",
        "classStat",
        "deprecated",
        "ppErrBits",
        "objID",
        "multiframeID",
        "extNum",
        "seqNum",
        "flag",
        "modelDistSecs",
    ]
    detection_arrayvals_df = make_array_cols(
        detection_df,
        key="sourceID",
        filter_col="filterID",
        order_by="sourceID",
        cols_to_transform=columns_to_array_value,
    )

    bucket_save(
        df=detection_arrayvals_df,
        buckets=BUCKETS,
        key="sourceID",
        table_name="detection_arrays_bucketed",
        spark=spark,
    )


@dg.asset(
    deps=["vvv_src5"],
    required_resource_keys={"spark"},
)
def source_bucketed(context: AssetExecutionContext):
    spark = context.resources.spark
    source_df = spark.read.parquet(DESTINATION + "/vvvSrc5/mod0000")
    bucket_save(
        df=source_df,
        buckets=BUCKETS,
        key="sourceID",
        table_name="source_bucketed",
        spark=spark,
    )


@dg.asset(
    deps=["detection_array_valued_bucketed", "source_bucketed"],
    required_resource_keys={"spark"},
)
def source_detection_joined(context: AssetExecutionContext):
    spark = context.resources.spark

    tables = spark.catalog.listTables()
    for table in tables:
        print(f"{table.name} ({table.tableType})")

    joined = spark.table("source_bucketed").join(
        spark.table("detection_arrays_bucketed"), on="sourceID"
    )

    joined = cast_df_using_schema(df=joined, schema=schema_joined_source_detection)

    bucket_save(
        joined,
        buckets=BUCKETS,
        key="sourceID",
        table_name="source_detection_joined",
        spark=spark,
    )
