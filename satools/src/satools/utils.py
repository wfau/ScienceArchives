import os


def is_correctly_bucketed(table_name, spark, buckets, key):
    buckets_df = get_bucketing_data(table_name, spark)

    if not int(buckets_df["n_buckets"]) == int(buckets):
        raise ValueError(
            f"Not correctly bucketed - expected {buckets} buckets but found {int(buckets_df['n_buckets'])}"
        )

    elif not list(buckets_df["bucket_col"]) == list(key):
        raise ValueError(
            f"Not correctly bucketed - expected {key} as bucketing col but found {buckets_df['bucket_col']}"
        )
    else:
        return True


def count_parquet_files(table_name):
    table_path = os.path.join("spark-warehouse", table_name)
    return sum(1 for f in os.listdir(table_path) if f.endswith(".parquet"))


def get_bucketing_data(table_name, spark):
    bucketing_data = {}
    desc = spark.sql(f"DESCRIBE TABLE EXTENDED {table_name}").collect()

    for row in desc:
        if "Num Buckets" in row.col_name:
            bucketing_data["n_buckets"] = row.data_type
        elif "Bucket Columns" in row.col_name:
            bucketing_data["bucket_col"] = row.data_type.strip("`[]")

    return bucketing_data
