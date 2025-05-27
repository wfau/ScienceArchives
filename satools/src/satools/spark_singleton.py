from pyspark.sql import SparkSession


class SparkSingleton:
    """Singleton class for SparkSession. Usable as `SparkSingleton.get_spark(...)` or `with SparkSingleton(...) as spark`."""

    _spark = None

    def __init__(
        self,
        app_name: str = "SparkApp",
        n_cores: int = 4,
        driver_memory: str = "30g",
        warehouse_dir: str = "spark-warehouse",
    ):
        self.app_name = app_name
        self.n_cores = n_cores
        self.driver_memory = driver_memory
        self.warehouse_dir = warehouse_dir

    def build_session(self):
        return (
            SparkSession.builder.appName(self.app_name)
            .master(f"local[{self.n_cores}]")
            .config("spark.driver.memory", self.driver_memory)
            .config("spark.sql.warehouse.dir", self.warehouse_dir)
            .config("spark.sql.catalogImplementation", "hive")
            .config(
                "javax.jdo.option.ConnectionURL", "jdbc:derby:metastore_db;create=true"
            )
            .enableHiveSupport()
            .getOrCreate()
        )

    @classmethod
    def get_spark(cls, **kwargs):
        if cls._spark is None:
            instance = cls(**kwargs)
            cls._spark = instance.build_session()
        return cls._spark

    @classmethod
    def stop_spark(cls):
        if cls._spark is not None:
            cls._spark.stop()
            cls._spark = None

    def __enter__(self):
        if self._spark is None:
            self._spark = self.build_session()
        return self._spark

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._spark.stop()
        SparkSingleton._spark = None
        self._spark = None
