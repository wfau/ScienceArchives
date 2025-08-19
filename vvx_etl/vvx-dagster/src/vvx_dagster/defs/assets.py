import dagster as dg
from dagster import AssetExecutionContext
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType
from pyspark.sql.functions import lit
from typing import Set

from ..transformations.array_columns import make_array_cols
from ..transformations.utils import cast_df_using_schema
from ..schema.schema_vvv_src5 import schema_vvv_src5
from ..schema.schema_joined_qppv import schema_joined_qppv
from ..transformations.extract import download_parquets, get_mods

from .resources import SparkResource
from .configs import CONFIG


# Define partitions for each table
qppv_partitions = dg.DynamicPartitionsDefinition(name="qppv_mods")
vvv_src5_partitions = dg.DynamicPartitionsDefinition(name="vvv_src5_mods")
joined_mods = dg.DynamicPartitionsDefinition(name="joined_mods")


def download_parquets_to_spark(
    spark: SparkResource, schema: StructType, table_name: str, mod: str
):

    download_parquets(
        base_url=CONFIG.base_url,
        table_name=table_name,
        mod=mod,
        output_path=CONFIG.download_dir,
    )

    spark_session = spark.get_session()
    df = (
        spark_session.read.option("mergeSchema", "true")
        .schema(schema)
        .parquet(f"{CONFIG.download_dir}/{table_name}/*")
    )

    df_with_mod = df.withColumn("sourceID_mod", lit(mod))
    df_with_mod.write.saveAsTable(
        name=table_name, format="parquet", mode="append", partitionBy="sourceID_mod"
    )


@dg.asset(partitions_def=qppv_partitions)
def joined_qppv(context: AssetExecutionContext, spark: SparkResource) -> None:
    mod = context.partition_key
    download_parquets_to_spark(
        spark, schema=schema_joined_qppv, table_name="JoinedQPPV", mod=mod
    )


@dg.asset(partitions_def=vvv_src5_partitions)
def vvv_src5(context: AssetExecutionContext, spark: SparkResource) -> None:
    mod = context.partition_key
    download_parquets_to_spark(
        spark, schema=schema_vvv_src5, table_name="vvvSrc5", mod=mod
    )


@dg.asset(deps=["joined_qppv"], partitions_def=qppv_partitions)
def detection_array_valued(
    context: AssetExecutionContext, spark: SparkResource
) -> None:
    mod = context.partition_key
    spark_session = spark.get_session()

    df = spark_session.table("joined_qppv")

    transformed = make_array_cols(
        df,
        key="sourceID",
        filter_col="filterID",
        order_by="sourceID",
        cols_to_transform=CONFIG.columns_to_transform,
    )

    df.write.saveAsTable(
        name="Detection_Arrayvals",
        format="parquet",
        mode="append",
        partitionBy="sourceID_mod",
    )


@dg.asset(deps=["detection_array_valued", "vvv_src5"], partitions_def=joined_mods)
def source_detection_joined(context: dg.AssetExecutionContext, spark: SparkResource):
    mod = context.partition_key
    spark_session = spark.get_session()

    detection_df = spark_session.table("Detection_Arrayvals")
    vvv_src5_df = spark_session.table("vvvSrc5")

    joined_df = vvv_src5_df.join(detection_df, on="sourceID")
    cast_df = cast_df_using_schema(joined_df, schema=schema_joined_source_detection)

    cast_df.write.saveAsTable(
        name="Source_Detection_Joined",
        format="parquet",
        mode="append",
        partitionBy="sourceID_mod",
    )
