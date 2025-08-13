import dagster as dg
from pathlib import Path
from ..transformations.array_columns import make_array_cols
from ..transformations.bucketing import bucket_save
from ..transformations.utils import cast_df_using_schema
from ..transformations.schema import schema_joined_source_detection

from ..transformations.extract import download_parquets
import pandas as pd
from dagster import asset, AssetExecutionContext
from pyspark.sql import SparkSession
from typing import List
from .resources import SparkResource
from .configs import CONFIG


@dg.asset
def joined_qppv() -> None:
    download_parquets(url=CONFIG.qppv_url, output_path=CONFIG.download_dir)


@dg.asset
def vvv_src5() -> None:
    download_parquets(url=CONFIG.vvv_src5_url, output_path=CONFIG.download_dir)


@dg.asset(deps=["joined_qppv"])
def detection_array_valued_bucketed(spark: SparkResource):
    spark_session = spark.get_session()
    detection_df = spark_session.read.option("mergeSchema", "true").parquet(
        CONFIG.download_dir + "/JoinedQPPV/*"
    )

    detection_arrayvals_df = make_array_cols(
        detection_df,
        key="sourceID",
        filter_col="filterID",
        order_by="sourceID",
        cols_to_transform=CONFIG.columns_to_transform,
    )

    bucket_save(
        df=detection_arrayvals_df,
        buckets=CONFIG.n_buckets,
        key="sourceID",
        table_name="detection_arrays_bucketed",
        spark=spark_session,
    )


@dg.asset(deps=["vvv_src5"])
def source_bucketed(spark: SparkResource):
    spark_session = spark.get_session()
    print("path", CONFIG.download_dir + "/vvvSrc5")
    source_df = spark_session.read.option("mergeSchema", "true").parquet(
        CONFIG.download_dir + "/vvvSrc5/*"
    )

    bucket_save(
        df=source_df,
        buckets=CONFIG.n_buckets,
        key="sourceID",
        table_name="source_bucketed",
        spark=spark_session,
    )


@dg.asset(
    deps=["detection_array_valued_bucketed", "source_bucketed"],
)
def source_detection_joined(spark: SparkResource):
    spark_session = spark.get_session()

    tables = spark_session.catalog.listTables()
    for table in tables:
        print(f"{table.name} ({table.tableType})")

    joined = spark_session.table("source_bucketed").join(
        spark_session.table("detection_arrays_bucketed"), on="sourceID"
    )

    joined = cast_df_using_schema(df=joined, schema=schema_joined_source_detection)

    bucket_save(
        joined,
        buckets=CONFIG.n_buckets,
        key="sourceID",
        table_name="source_detection_joined",
        spark=spark_session,
    )
