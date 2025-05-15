from pyspark.sql import SparkSession

class SparkSingleton:
    _spark = None

    @classmethod
    def get_spark(cls):
        if cls._spark is None:
            cls._spark = SparkSession.builder \
                .appName("MySingletonSparkApp") \
                .master("local[*]") \
                .config("spark.driver.memory", "8g") \
                .enableHiveSupport() \
                .getOrCreate()
        return cls._spark

    @classmethod
    def stop_spark(cls):
        if cls._spark is not None:
            cls._spark.stop()
            cls._spark = None

    def __enter__(self):
        self._spark = self.get_spark()
        return self._spark

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_spark()