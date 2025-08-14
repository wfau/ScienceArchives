from pyspark.sql.types import *

schema_vvv_src5 = StructType(
    [
        StructField("sourceID", LongType(), True),
        StructField("filterID", ShortType(), True),
        StructField("mjd", DoubleType(), True),
        StructField("aperMag1", FloatType(), True),
        StructField("aperMag1err", FloatType(), True),
        StructField("aperMag2", FloatType(), True),
        StructField("aperMag2err", FloatType(), True),
        StructField("aperMag3", FloatType(), True),
        StructField("aperMag3err", FloatType(), True),
        StructField("errBits", IntegerType(), True),z
        StructField("averageConf", FloatType(), True),
        StructField("class", ShortType(), True),
        StructField("classStat", FloatType(), True),
        StructField("deprecated", ShortType(), True),
        StructField("ppErrBits", IntegerType(), True),
        StructField("flag", ShortType(), True),
        StructField("modelDistSecs", DoubleType(), True),
        StructField("objID", LongType(), True),
        StructField("multiframeID", LongType(), True),
        StructField("extNum", ShortType(), True),
        StructField("seqNum", IntegerType(), True),
    ]
)
