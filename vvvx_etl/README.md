# ETL pipeline for VVVZ

ETL pipeline for transforming VVVX data to new data model. 

## Contributors
* Simon Harnqvist (sharnqvi@roe.ac.uk)

## Organisation
Code lives in `etl`. Key modules are:
* `source_detection_etl.py` - transforms table `vvvDetection` to have array-valued columns, and then joins with `vvvSource` to make a single wide table for easier querying.
* `array_columns.py` - code for array-valued column transformation
* `bucketing.py` - saves tables in bucketed format, allowing faster joins in Spark
* `spark_singleton.py` - singleton class for SparkSession with suitable Hive settings etc

Other modules provide the expected schema, various utils, errors, etc.

If/when additional ETL pipelines are added, dividing these into suitable subdirectories would be helpful.

### Tests and validation

There are current two sets of tests:
* Unit tests for `array_columns.py` and `bucketing.py` in `tests/`
* Integration and a full end-to-end test for `source_detection_etl.py` is in `tests/test_source_detection_etl.py`

Perhaps more importantly, automatic validation runs throughout `etl/source_detection_etl.py`, with a final set of validation on the loaded output dataset

## Usage information

Install with `pip install -e .` from this directory (`etl`)

Settings are configured with a file `etl_config.toml` that must live in the relevant working directory. A CLI option to set to path might be useful in future.

Example `etl_config.toml`:
```toml

title = "ScienceArchives pipeline config"

[spark_warehouse]
path = "spark-warehouse"
overwrite = true

[parquet_paths]
source = "ScienceArchives/etl/example_data/source"
detection = "ScienceArchives/etl/example_data/detection"

[table_names]
source = "source"
detection = "detection"
source_detection = "source_detection"

[partitioning]
n_buckets = 8

[transform]
columns_to_array_value = [
        "mjd",
        "aperMag1",
        "aperMag1err",
        "aperMag2",
        "aperMag2err",
        "aperMag3",
        "aperMag3err",
        "errBits",
        "averageConf",
        "class",
        "classStat",
        "deprecated",
        "ppErrBits",
        "objID",
        "multiframeID",
        "extNum",
        "seqNum",
        "flag",
        "modelDistSecs",
]
```

### Dependencies

The local conda environment used is available in `spark355.yaml` for reference.

The only key external dependencies are `PySpark = 3.5.5`, `toml`, and `pytest`. See the YAML if specific versions are required.
