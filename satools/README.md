# satools: Common Database & Archive Curation tools Python modules

### Installation
`pip install -e .`

### Current modules in `src/satools`
* `array_columns.py`: Transform passband data from float to array-valued columns.
* `bucketing.py`: Save tables in Spark, bucketed by some key.
* `spark_singleton.py`: Default singleton for Spark
* `utils.py`: Currently, helper functions for tests. (Could perhaps move into test dir?)

### Tests

🔧 **Integration Tests** (`integration_test.py`)

This project includes a PySpark-based integration test suite using pytest to verify core data processing logic.

What’s tested:

* Bucketed table creation (bucket_save)
* Array column transformation (make_array_cols)
* Join correctness and efficiency (ensuring no shuffle)
* Data integrity checks (e.g., number of observations match expected)
* Schema validation (e.g., array of floats)

How it's run:
* Uses temporary Spark warehouse paths via pytest fixtures
* Runs on small test datasets stored in tests/example_data/
* Avoids broadcast joins to validate sort-merge joins

<br>


🔧 **Unit Tests** (`test_bucketing.py` and `test_array_columns.py`) <br>
* Standard unit tests on self-contained dummy data.