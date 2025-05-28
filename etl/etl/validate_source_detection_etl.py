from etl.errors import *
from etl.utils import is_correctly_bucketed, count_parquet_files
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType


def validate_consistent_nrows(original: DataFrame, final: DataFrame) -> None:
    if original.count() != final.count():
        raise InconsistentRowCountError(
            f"Transformed dataframe does not have the same number of rows ({final.count()}) as the original {original.count()}"
        )


def validate_schema(expected: StructType, observed: StructType) -> None:
    if expected != observed:
        raise InconsistentSchemaError(
            "Schema not matching expected. Found: \n {observed} \n Expected: {expected} \n"
        )


def validate_bucketing(table_name: str, buckets, key: str, spark: SparkSession) -> None:
    is_correctly_bucketed(table_name, spark, buckets, key)

    n_parquet_files = count_parquet_files(spark=spark, table_name=table_name)
    if n_parquet_files != buckets:
        raise BucketingError(
            f"Number of buckets ({buckets}) does not correspond to the number of parquet files ({n_parquet_files})"
        )
