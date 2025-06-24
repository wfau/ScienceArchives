from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, expr
from pyspark.sql.types import *
from vvx_etl.errors import TableNotInCatalogError, BucketingError
import os
import re


def check_table_is_in_catalog(table_name: str, spark: SparkSession) -> None:
    if not table_name in [t.name for t in spark.catalog.listTables()]:
        raise TableNotInCatalogError(
            f"Table {table_name} not found in Spark catalog. Found tables: {spark.catalog.listTables()}. Database: {spark.catalog.currentDatabase()}"
        )


def get_table_location(spark: SparkSession, table_name: str) -> str:
    """Get the physical location of a Spark SQL table."""
    desc = spark.sql(f"DESCRIBE TABLE EXTENDED {table_name}").collect()
    for row in desc:
        if row.col_name.strip().lower() == "location":
            return row.data_type
    raise ValueError(f"Could not find location for table {table_name}")


def count_parquet_files(spark: SparkSession, table_name: str) -> int:
    """Count number of parquet files that a table is partitioned into."""
    table_path = get_table_location(spark, table_name)
    if table_path.startswith("file:"):
        table_path = table_path.replace("file:", "", 1)
    try:
        return sum(1 for f in os.listdir(table_path) if f.endswith(".parquet"))
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Directory {table_path} not found. Is the table created?"
        )


def get_bucketing_data(spark: SparkSession, table_name: str) -> dict:
    """Get bucketing information from Spark SQL table metadata."""
    bucketing_data = {}
    desc = spark.sql(f"DESCRIBE TABLE EXTENDED {table_name}").collect()

    for row in desc:
        if "Num Buckets" in row.col_name:
            bucketing_data["n_buckets"] = int(row.data_type.strip())
        elif "Bucket Columns" in row.col_name:
            bucketing_data["bucket_col"] = row.data_type.strip("`[]").split(", ")

    return bucketing_data


def is_correctly_bucketed(
    spark: SparkSession, table_name: str, buckets: int, key: str
) -> True:
    """Check whether a table is bucketed correctly by bucket count and column."""
    info = get_bucketing_data(table_name, spark)

    if info.get("n_buckets") != buckets:
        raise BucketingError(
            f"Expected {buckets} buckets, but found {info.get('n_buckets')}"
        )

    if [key] != info.get("bucket_col", []):
        raise BucketingError(
            f"Expected bucket column {key}, but found {info.get('bucket_col')}"
        )

    return True


def sanitise_identifier(identifier: str) -> str:
    """Prevent SQL injection by ensuring identifier does not contain dangerous chars"""
    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", identifier):
        return identifier
    else:
        raise ValueError(f"Invalid SQL identifier: {identifier}")


def cast_df_using_schema(df: DataFrame, schema: StructType) -> DataFrame:
    """
    Casts the columns of a Spark DataFrame to match the provided schema,
    including correct handling of array element casting and nullability.

    This function:
    - Casts columns to the target data type if they differ.
    - Handles casting of array element types using `transform()`.
    - Preserves or updates column nullability to match the provided schema.

    Parameters:
    ----------
    df : pyspark.sql.DataFrame
        The input DataFrame whose columns need to be cast.
    schema : pyspark.sql.types.StructType
        The desired schema, including field names, data types, and nullability.

    Returns:
    -------
    pyspark.sql.DataFrame
        A DataFrame with columns cast to match the provided schema.
    """
    current_schema = dict(df.dtypes)

    new_cols = []
    for field in schema.fields:
        field_name = field.name
        target_dtype = field.dataType
        target_nullable = field.nullable
        current_dtype = current_schema.get(field_name)

        if isinstance(target_dtype, ArrayType):
            # Handle array casting using transform()
            target_elem_type_str = target_dtype.elementType.simpleString()
            expr_str = (
                f"transform({field_name}, x -> cast(x as {target_elem_type_str}))"
            )
            new_col = expr(expr_str).alias(field_name)

        elif current_dtype != target_dtype.simpleString():
            # Cast primitive types directly
            new_col = col(field_name).cast(target_dtype).alias(field_name)

        else:
            new_col = col(field_name)

        new_cols.append(new_col)

    return df.select(new_cols)


def strip_nullability(data_type: DataType) -> DataType:
    """
    Recursively returns a version of the data type with all nullability removed,
    including nested types like ArrayType, MapType, StructType.
    """
    if isinstance(data_type, ArrayType):
        return ArrayType(strip_nullability(data_type.elementType), containsNull=False)
    elif isinstance(data_type, MapType):
        return MapType(
            strip_nullability(data_type.keyType),
            strip_nullability(data_type.valueType),
            valueContainsNull=False,
        )
    elif isinstance(data_type, StructType):
        return StructType(
            [
                StructField(f.name, strip_nullability(f.dataType), nullable=False)
                for f in data_type.fields
            ]
        )
    else:
        return data_type


def check_schema_alignment(expected: StructType, observed: StructType) -> None:
    """Check that schema matches provided, ignoring nullability since Spark will not enforce that"""

    failing_cols = []

    observed_fields = {field.name: field.dataType for field in observed.fields}

    for field in expected.fields:
        expected_vals = (field.name, strip_nullability(field.dataType))
        observed_raw_type = observed_fields.get(field.name)

        if observed_raw_type is None:
            observed_vals = ("<missing>", None)
        else:
            observed_vals = (field.name, strip_nullability(observed_raw_type))

        if expected_vals != observed_vals:
            failing_cols.append((expected_vals, observed_vals))

    if failing_cols:
        mismatch_details = "\n".join(
            f"Expected: {e}, Observed: {o}" for e, o in failing_cols
        )
        raise InconsistentSchemaError(
            f"Schema not matching expected.\n\nMismatched columns:\n{mismatch_details}"
        )
