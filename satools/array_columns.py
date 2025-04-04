from pyspark import sql
from pyspark.sql.functions import collect_list
from functools import reduce

def transform_passbands(df: sql.DataFrame, filter_col: str = "filterID", new_col_name: str = "passband"):
    """Convert numeric filter references to letter-encoded passbands"""
    passbands_dict = {"1": "Z",
                      "2": "Y",
                      "3": "J",
                      "4": "H",
                      "5": "K",
                      "8": "blank"}
    return df.withColumn(new_col_name, df[filter_col].cast("string")).replace(passbands_dict, subset=[new_col_name])
    
def _rename_pivoted_columns(df: sql.DataFrame, col_name: str):
    """Append feature names to passband column names e.g. J -> J_mjd"""
    old_columns = df.columns[1:]
    new_columns = [col + f"_{col_name}" for col in old_columns]
    return reduce(lambda df, idx: df.withColumnRenamed(old_columns[idx], new_columns[idx]), range(len(old_columns)), df)

def pivot_aggregate_col(grouped_df: sql.group.GroupedData,
                     col_name: str, pivot_on: str = "passband") -> sql.DataFrame:
    """Aggregate column by key into lists and pivot on other column e.g. passband"""
    aggregated = grouped_df.pivot(pivot_on).agg(sql.functions.collect_list(col_name))
    return _rename_pivoted_columns(aggregated, col_name)


def merge_all(aggregated_dfs: list[sql.DataFrame],
              join_key: str) -> sql.DataFrame:
    """Sequentially merge all dataframes in list to single df."""
    return reduce(lambda df1, df2: df1.join(df2, on=join_key), aggregated_dfs)


def make_array_cols(df: sql.DataFrame, key: str, filter_col:str) -> sql.DataFrame:
    """Transform df to array-valued columns.

    Args:
        df (sql.DataFrame): Dataframe in wide format.
        key (str): Unique key to group by.
        filter_col (str): Column (int) containing passbands to pivot on

    Returns:
        sql.DataFrame: Dataframe with array-valued columns.
    """
    assert key in df.columns, f"Key {key} not in columns of dataframe {df}"
    df = transform_passbands(df, filter_col="filterID", new_col_name = "passband").drop(filter_col)
    grouped = df.groupBy(key)
    aggregated_dfs = [pivot_aggregate_col(grouped_df=grouped, col_name=col_name, pivot_on="passband")
                      for col_name in df.columns if col_name not in [key, "passband"]]
    return merge_all(aggregated_dfs, key)

