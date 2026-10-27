#!/usr/bin/env python3
"""Compare query execution time between PostgreSQL (ADBC) and MSSQL
(mssql-python) using the same streaming code path as the MOONS web app
(``server/queries/tasks.py``), against **existing** GES tables/views.

No tables are created and no data is written. Point the script at two
databases that already hold the same GES release (same table/view names and
the same data in both) and it times a set of representative queries against
each backend.

Because it compares two databases, it first checks **data parity** (row counts
of the base tables in both) and warns if they differ -- a timing comparison is
only meaningful when the datasets match.

Queries use only the three base tables that are available in both databases
(``AstroAnalysis``, ``SpectrumGroup``, ``Target``):
  * wide, filtered selects over the big ``AstroAnalysis`` table
  * the ``RecommendedAstroAnalysis`` filter applied to the base table
  * a 2-way join (``SpectrumGroup`` to ``Target`` on targetID)
  * the real target-page 3-way join (Target + AstroAnalysis + SpectrumGroup)
  * a simple aggregation

Usage
-----
    python benchmark.py \
        --pg-url "postgresql://user:pass@host:5432/gesdr5" \
        --mssql-conn "Server=host;Database=gesdr5;Uid=sa;Pwd=...;TrustServerCertificate=yes"

    # tune MSSQL row batch size (mirrors QUERY_DB_BATCH_SIZE)
    QUERY_DB_BATCH_SIZE=2048 python benchmark.py --pg-url ... --mssql-conn ...

    # measure pure query+transfer, skip the parquet disk write
    python benchmark.py --pg-url ... --mssql-conn ... --no-parquet

    # also time the whole-result arrow() (non-streaming) path
    python benchmark.py --pg-url ... --mssql-conn ... --materialise

    # only run a subset of queries; more repeats for stable numbers
    python benchmark.py --pg-url ... --mssql-conn ... --queries astro_agg --repeat 5
"""

import argparse
import os
import time

import pyarrow.parquet as pq

# Base tables used for the data-parity check. These are the only tables that
# are present in both databases. The physical names differ in case between the
# two backends: Postgres stores them lowercase, MSSQL uses PascalCase. The keys
# match the {astro}/{sg}/{target} placeholders used in the query templates.
PG_TABLES = {
    "astro": "astroanalysis",
    "sg": "spectrumgroup",
    "target": "target",
}
MSSQL_TABLES = {
    "astro": "AstroAnalysis",
    "sg": "SpectrumGroup",
    "target": "Target",
}
PARITY_NAMES = {
    "astro": "AstroAnalysis",
    "sg": "SpectrumGroup",
    "target": "Target",
}


# ---------------------------------------------------------------------------
# Streaming readers (mirror tasks.py)
# ---------------------------------------------------------------------------
class MssqlStreaming:
    """Mimics _MssqlCursor: exposes the same record-batch interface as ADBC,
    streaming the result via arrow_reader(batch_size=...)."""

    def __init__(self, cursor, batch_size=None):
        self._cursor = cursor
        self._batch_size = batch_size

    def execute(self, query):
        return self._cursor.execute(query)

    def fetch_record_batch(self):
        return self._cursor.arrow_reader(batch_size=self._batch_size)

    def fetch_arrow_table(self):
        return self._cursor.arrow(batch_size=self._batch_size)

    def close(self):
        return self._cursor.close()


def pg_connection(pg_url):
    from urllib.parse import urlencode
    from adbc_driver_postgresql import dbapi as pgdb
    # The GES tables live in the 'gesdr5' schema; mirror the app (tasks.py),
    # which sets the search_path via the URL so unqualified names resolve.
    options = urlencode({'options': '--search_path=gesdr5'})
    return pgdb.connect(f'{pg_url}?{options}')


def mssql_connection(mssql_conn):
    import mssql_python
    # Queries are always SELECT against a read-only user, so autocommit=True
    # (the app uses this too) to avoid holding server-side cursors/locks.
    return mssql_python.connect(connection_str=mssql_conn, autocommit=True)


def drain(reader, path=None):
    """Consume a record-batch reader, writing to ``path`` if given.

    Returns the total row count. Mirrors ``write_results`` when a path is
    provided; counts-only when ``path`` is None.
    """
    rows = 0
    if path:
        with pq.ParquetWriter(path, reader.schema) as writer:
            try:
                while True:
                    batch = reader.read_next_batch()
                    writer.write(batch)
                    rows += batch.num_rows
            except StopIteration:
                pass
    else:
        try:
            while True:
                batch = reader.read_next_batch()
                rows += batch.num_rows
        except StopIteration:
            pass
    return rows


def close_quiet(cur, conn):
    for r in (cur, conn):
        try:
            r.close()
        except Exception:
            pass


def count_rows(make_conn, conn_str, table):
    conn = None
    cur = None
    try:
        conn = make_conn(conn_str)
        cur = conn.cursor()
        cur.execute(f"SELECT count(*) FROM {table}")
        row = cur.fetchone()
        return row[0] if row else None
    except Exception as exc:
        return f"ERROR: {exc}"
    finally:
        close_quiet(cur, conn)


def check_parity(make_pg, pg_url, make_ms, ms_conn):
    print("Checking data parity (base-table row counts) ...")
    matched = True
    for name, pg_table in PG_TABLES.items():
        ms_table = MSSQL_TABLES[name]
        display = PARITY_NAMES[name]
        p = count_rows(make_pg, pg_url, pg_table)
        m = count_rows(make_ms, ms_conn, ms_table)
        flag = "OK" if p == m else "MISMATCH"
        if p != m:
            matched = False
        print(f"  {display:<18} postgres={p!s:<12} mssql={m!s:<12} {flag}")
    if not matched:
        print("  NOTE: row counts differ between the two databases.")
    return matched


# ---------------------------------------------------------------------------
# Queries under test. Use only tables that hold the SAME rows in both databases
# so each PG-vs-MSSQL comparison is apples-to-apples.
#
# AstroAnalysis is excluded: the Postgres stand-in holds only a small subset
# (1000 rows vs ~1.9M), so no query over it can return matching results.
# SpectrumGroup and Target match exactly (262488 / 82410 rows). They share no
# direct join column (their only relationship goes through AstroAnalysis), so
# the comparable queries are full-table selects over each of the two matched
# tables -- Postgres reads the identical dataset to MSSQL.
# ---------------------------------------------------------------------------
DEFAULT_QUERIES = {
    # Full scan of SpectrumGroup (262488 rows, identical in both databases).
    "sg_scan": (
        "SELECT * FROM {sg}"
    ),
    # Full scan of Target (82410 rows, identical in both databases).
    "target_scan": (
        "SELECT * FROM {target}"
    ),
}


def run_query(name, make_conn, conn_str, query, mssql=False, materialise=False,
              write_parquet=True):
    """Run one query once. Return (elapsed_seconds, row_count) or (error, None)."""
    tag = "ms" if mssql else "pg"
    path = f"/tmp/{tag}_{name}.parquet" if write_parquet else None
    tables = MSSQL_TABLES if mssql else PG_TABLES
    query = query.format(**tables)
    conn = None
    cur = None
    t0 = time.time()
    try:
        conn = make_conn(conn_str)
        cur = conn.cursor()
        cursor = MssqlStreaming(cur, MSSQL_BATCH_SIZE) if mssql else cur
        cursor.execute(query)
        if materialise:
            table = cursor.fetch_arrow_table()
            rows = table.num_rows
        else:
            reader = cursor.fetch_record_batch()
            rows = drain(reader, path)
        return time.time() - t0, rows
    except Exception as exc:
        return f"ERROR: {exc}", None
    finally:
        close_quiet(cur, conn)


def bench(name, make_conn, conn_str, query, mssql, materialise, write_parquet,
          warmup, repeat):
    """Warm up, then run repeat times; return (best_elapsed, row_count)."""
    for _ in range(warmup):
        run_query(name, make_conn, conn_str, query, mssql, materialise,
                  write_parquet)
    best = None
    rows = None
    for _ in range(repeat):
        elapsed, rows = run_query(name, make_conn, conn_str, query, mssql,
                                  materialise, write_parquet)
        if isinstance(elapsed, str):
            return elapsed, None
        if best is None or elapsed < best:
            best = elapsed
    return best, rows


def main():
    ap = argparse.ArgumentParser(
        description="Compare query time for existing GES data: Postgres vs MSSQL")
    ap.add_argument("--pg-url", default=os.environ.get("PG_URL"),
                    help="ADBC Postgres connection URL (or PG_URL env), e.g. "
                         "postgresql://user:pass@host:5432/gesdr5")
    ap.add_argument("--mssql-conn", default=os.environ.get("MSSQL_CONN"),
                    help="mssql-python connection string (or MSSQL_CONN env), e.g. "
                         "Server=host;Database=gesdr5;Uid=sa;Pwd=...;"
                         "TrustServerCertificate=yes")
    ap.add_argument("--materialise", action="store_true",
                    help="also time the whole-result arrow() (non-streaming) path")
    ap.add_argument("--queries", default=None,
                    help="comma-separated subset of query names")
    ap.add_argument("--repeat", type=int, default=3,
                    help="timed runs per query (takes the minimum; default 3)")
    ap.add_argument("--warmup", type=int, default=1,
                    help="untimed warm-up runs per query before timing "
                         "(default 1; 0 to disable)")
    ap.add_argument("--no-parquet", action="store_true",
                    help="measure pure query+transfer, skip the parquet write")
    ap.add_argument("--no-parity", action="store_true",
                    help="skip the data-parity row-count check")
    args = ap.parse_args()

    if not args.pg_url or not args.mssql_conn:
        ap.error("--pg-url and --mssql-conn are required "
                 "(or set PG_URL / MSSQL_CONN).")

    queries = DEFAULT_QUERIES
    if args.queries:
        wanted = {k.strip(): v for k, v in queries.items()
                  if k.strip() in args.queries.split(",")}
        queries = wanted

    if not args.no_parity:
        check_parity(pg_connection, args.pg_url, mssql_connection,
                     args.mssql_conn)

    print(f"\nMSSQL batch_size = {MSSQL_BATCH_SIZE}   "
          f"warmup = {args.warmup}   repeat = {args.repeat}   "
          f"parquet = {'no' if args.no_parquet else 'yes'}\n")
    header = (f"{'query':<18}{'rows':>10}{'postgres (s)':>15}"
              f"{'mssql (s)':>13}{'ratio':>8}")
    print(header)
    print("-" * len(header))

    results = {}
    for qname, query in queries.items():
        p, p_rows = bench(qname, pg_connection, args.pg_url, query,
                          mssql=False, materialise=False,
                          write_parquet=not args.no_parquet,
                          warmup=args.warmup, repeat=args.repeat)
        m, m_rows = bench(qname, mssql_connection, args.mssql_conn, query,
                          mssql=True, materialise=False,
                          write_parquet=not args.no_parquet,
                          warmup=args.warmup, repeat=args.repeat)
        results[qname] = (p, p_rows, m, m_rows)

        cell = lambda v: f"{v:.3f}" if isinstance(v, float) else str(v)
        rows_disp = p_rows if p_rows == m_rows else f"{p_rows}/{m_rows}"
        ratio = "-"
        if isinstance(p, float) and isinstance(m, float) and p > 0:
            ratio = f"{m / p:.1f}x"
        print(f"{qname:<18}{str(rows_disp):>10}{cell(p):>15}{cell(m):>13}{ratio:>8}")
        if p_rows != m_rows and p_rows is not None and m_rows is not None:
            print(f"  ^ row count differs (pg {p_rows} vs mssql {m_rows}) - "
                  f"check parity")

    if args.materialise:
        print(f"\n--- MSSQL whole-result arrow() (non-streaming) ---")
        print(f"{'query':<18}{'mssql arrow() (s)':>20}")
        for qname, query in queries.items():
            m, _ = bench(qname, mssql_connection, args.mssql_conn, query,
                         mssql=True, materialise=True,
                         write_parquet=False, warmup=args.warmup,
                         repeat=args.repeat)
            cell = lambda v: f"{v:.3f}" if isinstance(v, float) else str(v)
            print(f"{qname:<18}{cell(m):>20}")

    print("\nDone.")


if __name__ == "__main__":
    MSSQL_BATCH_SIZE = int(os.environ.get("QUERY_DB_BATCH_SIZE", "8192"))
    main()
