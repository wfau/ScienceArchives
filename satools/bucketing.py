# Adapted from: https://github.com/wfau/gaiadmpsetup/blob/main/gaiadmpsetup/gaiadmpstore.py

from pyspark.sql.types import *
from pyspark.sql import functions as f
from pyspark.sql import *
from ScienceArchives.satools.spark_singleton import SparkSingleton

NUM_BUCKETS = 8
DEFAULT_KEY = "sourceID"


def save_to_binned_parquets(
    df: DataFrame,
    output_path: str,
    table_name: str,
    mode: str = "error",
    buckets: int = NUM_BUCKETS,
    key=DEFAULT_KEY,
):
    """
    Save a PySpark DataFrame as a bucketed Parquet table, sorted within buckets by a specified key.

    The DataFrame is written to the specified output path as a table using bucketing. This can improve
    performance for joins and queries that involve the bucketed key. The table is also registered in
    the Hive metastore under the given name.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        The DataFrame to write to storage. (Required)
    output_path : str
        Absolute path to the directory where the Parquet files will be saved. (Required)
    table_name : str
        Name under which the table will be registered in the Hive metastore. (Required)
    mode : str, optional
        Save mode. Options include: 'error' (default), 'overwrite', 'append', 'ignore'.
        'error' fails if the path already exists.
    buckets : int, optional
        Number of buckets to use. Defaults to NUM_BUCKETS.
    key : str or list of str, optional
        Column or list of columns to use for both bucketing and sorting within each bucket.
        Defaults to DEFAULT_KEY. Must be present in the DataFrame.

    Notes
    -----
    - The output is written in Parquet format using Spark's bucketing support.
    - The resulting table can be queried via Spark SQL if Hive support is enabled.
    """

    df.write.format("parquet").mode(mode).bucketBy(buckets, key).sortBy(key).option(
        "path", output_path
    ).saveAsTable(table_name)


## This should not be necessary after saving as table???
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
