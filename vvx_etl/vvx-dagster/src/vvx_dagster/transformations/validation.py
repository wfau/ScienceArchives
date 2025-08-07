from .errors import *
from .utils import is_correctly_bucketed, count_parquet_files
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType, ArrayType, MapType, StructField, DataType


def validate_consistent_nrows(detection: DataFrame, final: DataFrame) -> None:

    detection_source_ids = set(
        detection.select("sourceID").distinct().rdd.flatMap(lambda x: x).collect()
    )
    final_source_ids = set(
        final.select("sourceID").distinct().rdd.flatMap(lambda x: x).collect()
    )

    if len(list(detection_source_ids - final_source_ids)) != 0:
        raise InconsistentRowCountError(
            f"Transformed dataframe does not have the same number of source IDs ({len(list(final_source_ids))}) as the original detection table ({len(list(detection_source_ids))})"
        )


def _strip_nullability(data_type: DataType) -> DataType:
    """
    Recursively returns a version of the data type with all nullability removed,
    including nested types like ArrayType, MapType, StructType.
    """
    if isinstance(data_type, ArrayType):
        return ArrayType(_strip_nullability(data_type.elementType), containsNull=False)
    elif isinstance(data_type, MapType):
        return MapType(
            _strip_nullability(data_type.keyType),
            _strip_nullability(data_type.valueType),
            valueContainsNull=False,
        )
    elif isinstance(data_type, StructType):
        return StructType(
            [
                StructField(f.name, _strip_nullability(f.dataType), nullable=False)
                for f in data_type.fields
            ]
        )
    else:
        return data_type


def validate_schema(expected: StructType, observed: StructType) -> bool:
    """Check that schema matches provided, ignoring nullability since Spark will not enforce that"""

    failing_cols = []

    observed_fields = {field.name: field.dataType for field in observed.fields}

    for field in expected.fields:
        expected_vals = (field.name, _strip_nullability(field.dataType))
        observed_raw_type = observed_fields.get(field.name)

        if observed_raw_type is None:
            observed_vals = ("<missing>", None)
        else:
            observed_vals = (field.name, _strip_nullability(observed_raw_type))

        if expected_vals != observed_vals:
            failing_cols.append((expected_vals, observed_vals))

    if failing_cols:
        mismatch_details = "\n".join(
            f"Expected: {e}, Observed: {o}" for e, o in failing_cols
        )
        f"Schema not matching expected.\n\nMismatched columns:\n{mismatch_details}"
        return False
        # raise InconsistentSchemaError(
        #     f"Schema not matching expected.\n\nMismatched columns:\n{mismatch_details}"
        # )
    else:
        return True


def validate_bucketing(table_name: str, buckets, key: str, spark: SparkSession) -> bool:
    correctly_bucketed: bool = is_correctly_bucketed(
        spark=spark, table_name=table_name, buckets=buckets, key=key
    )
    n_parquet_files = count_parquet_files(spark=spark, table_name=table_name)
    if correctly_bucketed and n_parquet_files == buckets:
        return True
    else:
        return False
