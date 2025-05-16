def bucket_save(df, buckets, key, table_name, spark):
    df = df.repartition(buckets, key)
    df.createOrReplaceTempView("tmp_view")
    spark.sql(
        f"""
        CREATE TABLE {table_name}
        USING PARQUET
        CLUSTERED BY ({key}) INTO {buckets} BUCKETS
        AS SELECT * FROM tmp_view
    """
    )
