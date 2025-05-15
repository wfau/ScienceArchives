# Adapted from: https://github.com/wfau/gaiadmpsetup/blob/main/gaiadmpsetup/gaiadmpstore.py

from pyspark.sql.types import *
from pyspark.sql import functions as f
from pyspark.sql import *
from ScienceArchives.satools.spark_singleton import SparkSingleton

NUM_BUCKETS = 2048
DEFAULT_KEY = "sourceID"


def save_to_binned_parquets(
    df,
    outputParquetPath,
    table_name: str,
    mode="error",
    buckets=NUM_BUCKETS,
    bucket_and_sort_key=DEFAULT_KEY,
):
    """
    Save a data frame to a set of bucketed parquet files, repartitioning beforehand and sorting
    (by default on DPAC Gaia source UID) within the buckets.

    Parameters
    ----------
    df : DataFrame
        (mandatory) the data frame to be written to the persistent file store
    outputParquetPath : str
        (mandatory) the absolute path name of the folder to contain the files
    mode : str
        (optional) the mode for the underlying DataFrame write method (default : error, i.e. no silent failures)
    buckets : int
        (optional) the number of buckets (if in doubt leave as the default)
    bucket_and_sort_key : str
        (optional) the bucketing and sorting key for the keyed/clustered data (default source_id; you must specify
        an alternative if the data frame does not have this column present)
    """
    df.write.format("parquet").mode(mode).bucketBy(buckets, bucket_and_sort_key).sortBy(
        bucket_and_sort_key
    ).option("path", outputParquetPath).saveAsTable(table_name)


def reattachParquetFileResourceToSparkContext(
    table_name,
    file_path,
    schema_structures,
    cluster_key=DEFAULT_KEY,
    sort_key=DEFAULT_KEY,
    buckets=NUM_BUCKETS,
):
    # '''
    # Creates a Spark (in-memory) meta-record for the table resource specified for querying
    # through the PySpark SQL API.

    # Default assumption is that the table contains the Gaia source_id attribute and that the files have
    # been previously partitioned, bucketed and sorted on this field in parquet format
    # - see function saveToBinnedParquet().  If the table name specified already exists in the
    # catalogue IT WILL BE REMOVED (but the underlying data, assumed external, will remain).

    # Parameters
    # ----------
    # table_name : str
    # 	The table name to be used as the identifier in SQL queries etc.
    # file_path : str
    # 	The full disk file system path name to the folder containing the parquet file set.
    # schema_structures : StructType
    # 	One or more schema structures expressed as a StructType object containing a list of
    # 	StructField(field_name : str, type : data_type : DataType(), nullable : boolean)
    # cluster_key : str (optional)
    #     The clustering key (= bucketing and sort key) in the partitioned data set on disk.
    #     Default is Gaia catalogue source UID (= source_id).
    # sort_key : str (optional)
    #     The sorting key within buckets in the partitioned data set on disk.
    #     Default is Gaia catalogue source UID (= source_id).
    # buckets : int (optional)
    #     Number of buckets into which the data is organised.
    # '''

    with SparkSingleton() as spark:
        # put in the columns and their data types ...
        table_create_statement = "CREATE TABLE " + table_name + " ("
        for field in schema_structures:
            table_create_statement += (
                " `" + field.name + "` " + field.dataType.simpleString() + ","
            )
        # ... zapping that extraneous comma at the end
        table_create_statement = table_create_statement[:-1]

        # append the organisational details
        table_create_statement += ") USING parquet OPTIONS (path '" + file_path + "') "
        table_create_statement += (
            "CLUSTERED BY (%s) SORTED BY (%s) INTO %d"
            % (cluster_key, sort_key, buckets)
            + " BUCKETS"
        )

        # scrub any existing record - N.B. tables defined in this way are EXTERNAL, so this statement will not scrub
        # the underlying file data set. Also if the table doesn't exist, this will silently do nothing (no exception
        # will be thrown).
        spark.sql("DROP TABLE IF EXISTS " + table_name)

        # create the table resource
        spark.sql(table_create_statement)


# import copy

# def create_interim_schema_for_csv(schema_structure):
#     '''
#     Takes a schema StructType() and substitutes all array types as a string in order
#     to create a schema against which csv files can be read into an interim data frame
#     prior to conversion of the comma-separated string of numerical values into an array
#     of the appropriate numeric type.

#     Parameters
#     ----------
#     schema_structure : StructType
#         the table schema containing array types

#     Returns: StructType
#     -------------------
#     An edited version of the given schema with all ArrayType changed to StringType
#     '''

#     # new interim structure
#     interim_structure = StructType()

#     # iterate over the schema, copying in everything and substituting strings for any arrays
#     for field in schema_structure:
#         interim_field = copy.deepcopy(field)
#         if type(interim_field.dataType) == ArrayType: interim_field.dataType = StringType()
#         interim_structure.add(interim_field)

#     return interim_structure

# def cast_to_array(data_frame : DataFrame, column_name : str, data_type : DataType):
#     '''
#     Casts the specified string column in the given data frame into an
#     array with the specified data type. Assumes the string column contains
#     comma-separated values in plain text delimited by braces (which are
#     ignored). The array column is appended to the existing column set while
#     the original string column is removed. The resulting data frame will
#     contain an array column with the same name as the original string
#     data column.

#     Parameters:
#     -----------
#     data_frame : DataFrame()
#         The PySpark data frame instance to be operated on
#     column_name : str
#         The column name that contains the array data as a plain text string of
#         comma-separated values
#     data_type : DataType()
#         The PySpark data structure data type which should be ArrayType(SomeType())

#     Returns:
#     --------
#     a new data frame containing the requested modification
#     '''

#     # a temporary working column name for the array
#     temporary_column_name = column_name + '_array_data'

#     # reformat the string csv data as an array of the specified type
#     if isinstance(data_type.elementType, BooleanType):
#         # ... need to allow for the double quoted boolean labels
#         data_frame = data_frame.withColumn(temporary_column_name, f.split(f.col(column_name).substr(f.lit(3), f.length(f.col(column_name)) - 3), '","').cast(data_type))
#     else:
#         data_frame = data_frame.withColumn(temporary_column_name, f.split(f.col(column_name).substr(f.lit(2), f.length(f.col(column_name)) - 2), ',').cast(data_type))

#     # drop the original string column to save space
#     data_frame = data_frame.drop(column_name)

#     # rename the temporary column with the original column name
#     data_frame = data_frame.withColumnRenamed(temporary_column_name, column_name)

#     return data_frame


# def reorder_columns(data_frame : DataFrame, data_structure : StructType):
#     '''
#     Reorder the columns according to the Gaia archive public schema and so that
#     the parquet files can be re-attached against that standard schema.

#     Parameters:
#     -----------
#     data_frame : DataFrame()
#         The PySpark data frame instance to be operated on
#     data_structure : StructType()
#         The PySpark data structure containing the required schema definition

#     Returns:
#     --------
#     a new data frame with columns re-ordered according to that in the schema
#     '''

#     # use the schema to define the column order
#     ordered_columns = [field.name for field in data_structure]

#     # give it back in the schema-driven order
#     return data_frame.select(ordered_columns)


# def cast_all_arrays(data_frame : DataFrame, data_structure : StructType):
#     '''
#     Given an interim data frame read from csv and containing arrays in
#     plain text string representation, cycles over the schema transforming
#     all strings associated with arrays into the required primitive type.

#     Parameters:
#     -----------
#     data_frame : DataFrame()
#         The PySpark data frame instance to be operated on
#     data_structure : StructType()
#         The PySpark data structure containing the required schema definition

#     Returns:
#     --------
#     a new data frame with all arrays expressed as interim strings cast to their array structure type
#     '''

#     # cycle over the defined fields looking for arrays
#     for field in data_structure:

#         # if it's an array type then transmogrify:
#         if type(field.dataType) == ArrayType:
#             data_frame = cast_to_array(data_frame, field.name, field.dataType)

#     # finally reorder according to the original specification
#     return reorder_columns(data_frame, data_structure)
