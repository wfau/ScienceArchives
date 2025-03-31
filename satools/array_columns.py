from pyspark import sql
from pyspark.sql.functions import collect_list
from functools import reduce


def aggregate_by_key(grouped_df: sql.group.GroupedData,
                     col_name: str) -> sql.DataFrame:
    """Aggregate by key into lists e.g. (sourceID, [val1, val2, val3])"""
    return grouped_df.agg(collect_list(col_name).alias(col_name))


def merge_all(aggregated_dfs: list[sql.DataFrame],
              join_key: str) -> sql.DataFrame:
    """Sequentially merge all dataframes in list to single df."""
    return reduce(lambda df1, df2: df1.join(df2, on=join_key), aggregated_dfs)


def make_array_cols(df: sql.DataFrame, key: str) -> sql.DataFrame:
    """Transform df to array-valued columns.

    Args:
        df (sql.DataFrame): Dataframe in wide format.
        key (str): Unique key to group by.

    Returns:
        sql.DataFrame: Dataframe with array-valued columns.
    """
    assert key in df.columns, f"Key {key} not in columns of dataframe {df}"
    grouped = df.groupBy(key)
    aggregated_dfs = [aggregate_by_key(grouped_df=grouped, col_name=col_name)
                      for col_name in df.columns if col_name != key]
    return merge_all(aggregated_dfs, key)
