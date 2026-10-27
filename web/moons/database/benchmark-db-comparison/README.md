# Benchmark: PostgreSQL vs MSSQL query time

Standalone harness to measure query execution time for PostgreSQL (via ADBC)
vs Microsoft SQL Server (via `mssql-python`), using the **same streaming code
path as the MOONS web app** (`server/queries/tasks.py`).

It queries your **existing** GES tables/views — no tables are created and no
data is written. Both databases must already hold the same GES release (same
table/view names in both). The harness is fully separate from the app: its own
Dockerfile builds a Python image with the query drivers.

## Data parity (read this first)

Because it compares two *separate* databases, the comparison is only valid when
they hold the **same data**. On every run it first counts the base tables that
exist in both — `AstroAnalysis`, `SpectrumGroup`, `Target` — and prints the
counts side by side, noting if they differ. Only the tables that match are
timed (see below); a mismatch on any other table is reported so you know the
numbers for that table are not apples-to-apples. Use `--no-parity` to skip the
check.

## What it measures

Runs full-table scans over the tables that hold the **same rows in both
databases** (`SpectrumGroup`, `Target`), timing each against both backends.
`AstroAnalysis` is excluded: the Postgres stand-in only holds a small subset
(1000 rows vs ~1.9M in the real MSSQL), so any query over it returns different
results and would not be apples-to-apples. For each query it does a warm-up run
(untimed) then `--repeat` timed runs and reports the minimum, plus the row count
(so you can confirm both backends returned the same result set).

| Query         | What it does                                        |
|---------------|-----------------------------------------------------|
| `sg_scan`     | `SELECT * FROM SpectrumGroup` (262488 rows, identical in both DBs) |
| `target_scan` | `SELECT * FROM Target` (82410 rows, identical in both DBs) |

Postgres uses ADBC `fetch_record_batch()` streaming (app's `write_results`);
MSSQL uses `arrow_reader(batch_size=...)` streaming (app's `_MssqlCursor`).
The reported `ratio` is `mssql / postgres` elapsed time, so >1.0 = MSSQL slower.

## Run it

Point it at the two databases and run from a machine that can reach both:

```
PG_URL=postgresql://user:pass@db:5432/gesdr5 \
MSSQL_CONN='Server=mssql;Database=gesdr5;Uid=sa;Pwd=...;TrustServerCertificate=yes' \
docker compose up --build bench
```

or directly with Python:

```
pip install -r requirements.txt
python benchmark.py \
    --pg-url "postgresql://user:pass@db:5432/gesdr5" \
    --mssql-conn "Server=mssql;Database=gesdr5;Uid=sa;Pwd=...;TrustServerCertificate=yes"
```

### Useful options

```
# tune MSSQL row batch size (mirrors QUERY_DB_BATCH_SIZE)
QUERY_DB_BATCH_SIZE=2048 python benchmark.py --pg-url ... --mssql-conn ...

# measure pure query+transfer, skip the parquet disk write
python benchmark.py --pg-url ... --mssql-conn ... --no-parquet

# also time the whole-result arrow() (non-streaming) path
python benchmark.py --pg-url ... --mssql-conn ... --materialise

# only run a subset of queries; more repeats for stable numbers
python benchmark.py --pg-url ... --mssql-conn ... --queries astro_agg --repeat 5

# more warm-up runs (default 1), or disable parity check
python benchmark.py --pg-url ... --mssql-conn ... --warmup 2
python benchmark.py --pg-url ... --mssql-conn ... --no-parity
```

## Interpreting results

- **Parity first.** The parity check prints each table's row count in both
  databases. Only tables that match are timed; if the timed tables differ (a
  MISMATCH in the parity block), stop — the comparison is invalid for them.
- **Row counts per query** confirm both backends returned the same result set.
  A difference means the datasets differ (or a view resolved differently).
- **`ratio`** = `mssql / postgres` elapsed; >1.0 = MSSQL slower.
- Use `--materialise` to see whether the gap is in the streaming reader or in
  the whole-result `arrow()` path.
- Use `--no-parquet` to separate DB query+transfer time from the local parquet
  write.
- Note: indexes are *not* controlled here — the harness measures whatever your
  existing databases give.

## How it mirrors the app code

| App (`server/queries/tasks.py`)  | Benchmark                    |
|----------------------------------|------------------------------|
| `get_connection` (ADBC Postgres) | `pg_connection`              |
| `get_connection` (mssql, autocommit=True) | `mssql_connection`  |
| `_MssqlCursor.fetch_record_batch` | `MssqlStreaming.fetch_record_batch` |
| `write_results`                  | `drain`                      |
| `QUERY_DATABASE['BATCH_SIZE']`   | `QUERY_DB_BATCH_SIZE`        |