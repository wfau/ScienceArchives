#!/usr/bin/env python3
"""Copy a PostgreSQL database to Microsoft SQL Server via parquet.

Discovery-driven: enumerates all tables and views in the live Postgres
``information_schema`` (no hardcoded object list), so the MSSQL database
ends up identical to Postgres.

Each Postgres schema is a *data release* and maps to a separate MSSQL
database (one database per release). Within each MSSQL database, objects are
created in the default ``dbo`` schema.

Pipeline
--------
1. Discover tables + views (columns, types, primary keys, view definitions)
   from Postgres ``information_schema`` / ``pg_get_viewdef``.
2. Export each table's data to a parquet file (ADBC Postgres driver +
   pyarrow, the same streaming mechanism used by ``queries.tasks.write_results``).
3. Generate MSSQL DDL from the discovered Postgres schema.
4. Create a database per release, create tables/views, and load the parquet
   rows via mssql-python bulk copy.

Views are recreated as real MSSQL views (kept as-is; the GES view SQL is
dialect-neutral). ``RecommendedAstroAnalysis`` and any other view are included
automatically because views are discovered from the live database.

Requirements (see database/requirements.txt):
    adbc-driver-postgresql, pyarrow, mssql-python

Example
-------
    # NOTE: --postgres-url is the QUERY database (the one holding the GES
    # release schemas gesdr5/gesdr6), NOT the Django metadata database.
    # The Django app metadata (auth_*, django_*, queries_*, api_*) lives in the
    # 'public' schema of the Django database and is excluded from discovery.

    # one-shot: export, create databases + tables, and load
    python postgres_to_mssql.py \
        --postgres-url "postgresql://user:pass@db:5432/QUERY_DATABASE_NAME" \
        --mssql-conn "Server=mssql;Database=master;Uid=sa;Pwd=...;TrustServerCertificate=yes" \
        --outdir /tmp/pg2mssql \
        --create-databases --create-tables

    # separate export / import runs
    python postgres_to_mssql.py --postgres-url "..." --outdir /tmp/pg2mssql --skip-import
    python postgres_to_mssql.py --mssql-conn "..." --outdir /tmp/pg2mssql --skip-export --create-tables
"""

import argparse
import re
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

# Maps Postgres data_type (lowercased) to an MSSQL type.
# Format: (mssql_type_or_none, needs_length, needs_precision_scale)
#   mssql_type_or_none=None  -> unsupported, abort for that column
#   needs_length=True        -> NVARCHAR(n)/NCHAR(n) using character_maximum_length
#   needs_precision_scale=True -> DECIMAL(p,s) using numeric_precision/scale
PG_TO_MSSQL = {
    "bigint": ("BIGINT", False, False),
    "integer": ("INT", False, False),
    "int": ("INT", False, False),
    "int4": ("INT", False, False),
    "smallint": ("SMALLINT", False, False),
    "int2": ("SMALLINT", False, False),
    "real": ("REAL", False, False),
    "float4": ("REAL", False, False),
    "double precision": ("FLOAT", False, False),
    "float8": ("FLOAT", False, False),
    "float": ("FLOAT", False, False),
    "numeric": ("DECIMAL", False, True),
    "decimal": ("DECIMAL", False, True),
    "text": ("NVARCHAR(MAX)", False, False),
    "character varying": ("NVARCHAR", True, False),
    "varchar": ("NVARCHAR", True, False),
    "character": ("NCHAR", True, False),
    "char": ("NCHAR", True, False),
    "bpchar": ("NCHAR", True, False),
    "timestamp without time zone": ("DATETIME2", False, False),
    "timestamp with time zone": ("DATETIME2", False, False),
    "timestamp": ("DATETIME2", False, False),
    "date": ("DATE", False, False),
    "time without time zone": ("TIME", False, False),
    "time with time zone": ("TIME", False, False),
    "boolean": ("BIT", False, False),
    "bool": ("BIT", False, False),
    "uuid": ("UNIQUEIDENTIFIER", False, False),
    "bytea": ("VARBINARY(MAX)", False, False),
    "json": ("NVARCHAR(MAX)", False, False),
    "jsonb": ("NVARCHAR(MAX)", False, False),
}


def quote_ident(identifier):
    """Quote an identifier for MSSQL using brackets."""
    return f"[{identifier}]"


ARROW_TO_PG_TYPE = {
    pa.int64(): "bigint",
    pa.int32(): "integer",
    pa.int16(): "smallint",
    pa.int8(): "smallint",
    pa.float32(): "real",
    pa.float64(): "double precision",
    pa.bool_(): "boolean",
    pa.string(): "text",
    pa.binary(): "bytea",
}


def _column_from_arrow(field):
    """Convert an Arrow field to the column-dict shape used by mssql_type().

    Used when re-discovering objects from parquet files (--skip-export).
    """
    t = field.type
    data_type = "text"
    length = None
    precision = None
    scale = None
    if pa.types.is_timestamp(t):
        data_type = "timestamp"
    elif pa.types.is_date(t):
        data_type = "date"
    elif pa.types.is_time(t):
        data_type = "time without time zone"
    elif pa.types.is_decimal(t):
        data_type = "numeric"
        precision = t.precision
        scale = t.scale
    elif pa.types.is_large_string(t) or pa.types.is_string(t):
        data_type = "text"
        if hasattr(t, "max_length") and t.max_length:
            data_type = "character varying"
            length = t.max_length
    else:
        data_type = ARROW_TO_PG_TYPE.get(t, "text")
    return {
        "name": field.name,
        "data_type": data_type,
        "character_maximum_length": length,
        "numeric_precision": precision,
        "numeric_scale": scale,
        "is_nullable": "YES" if field.nullable else "NO",
    }


def quote_pg_ident(identifier):
    """Quote an identifier for PostgreSQL using double quotes."""
    return '"' + str(identifier).replace('"', '""') + '"'


def quote_table(schema, name):
    """PostgreSQL-qualified name (schema.object) using double-quote quoting."""
    if schema:
        return f"{quote_pg_ident(schema)}.{quote_pg_ident(name)}"
    return quote_pg_ident(name)


class Object:
    """A discovered Postgres table or view.

    ``schema`` is the Postgres schema, which maps to a separate MSSQL database
    (one database per data release). Within that MSSQL database, objects live in
    the default ``dbo`` schema, so the MSSQL object name omits the schema prefix.
    """

    def __init__(self, kind, schema, name, columns, primary_keys, view_definition=None):
        self.kind = kind  # 'table' or 'view'
        self.schema = schema  # Postgres schema == MSSQL database name
        self.name = name
        self.columns = columns  # list of dicts: name, data_type, max_length, precision, scale, nullable
        self.primary_keys = primary_keys  # list of column names
        self.view_definition = view_definition

    @property
    def qualified(self):
        """Postgres-qualified name (schema.object), used for export SELECT."""
        return quote_table(self.schema, self.name)

    @property
    def mssql_object(self):
        """MSSQL object name inside its database (dbo schema, no prefix)."""
        return quote_ident(self.name)

    @property
    def mssql_import_object(self):
        """Fully-qualified MSSQL destination (db.dbo.name) for bulkcopy.

        The bulk copy does not reliably inherit the ``USE`` database context, so
        it is given the database-qualified name to avoid resolving against the
        wrong (e.g. ``master``) database.
        """
        db = quote_ident(self.schema)
        return f"{db}.[dbo].{quote_ident(self.name)}"


def _sql_literal(value):
    """Escape a value as a Postgres string literal."""
    return "'" + str(value).replace("'", "''") + "'"


def discover(conn, schema_names):
    """Enumerate tables and views from Postgres information_schema."""
    cur = conn.cursor()
    objects = []

    # Build a set of schema filters. Empty list => all non-system, non-Django
    # schemas (the Django app metadata lives in 'public' and is not query data).
    if schema_names:
        placeholders = ",".join(f"'{s}'" for s in schema_names)
        schema_filter = f"AND t.table_schema IN ({placeholders})"
    else:
        schema_filter = (
            "AND t.table_schema NOT IN "
            "('pg_catalog', 'information_schema', 'public')"
        )

    # Tables first, then views (so view DDL references existing tables).
    table_sql = f"""
        SELECT t.table_schema, t.table_name
        FROM information_schema.tables t
        WHERE t.table_type = 'BASE TABLE' {schema_filter}
        ORDER BY t.table_schema, t.table_name
    """
    view_sql = f"""
        SELECT t.table_schema, t.table_name
        FROM information_schema.tables t
        WHERE t.table_type = 'VIEW' {schema_filter}
        ORDER BY t.table_schema, t.table_name
    """

    col_sql = """
        SELECT c.column_name, c.data_type, c.character_maximum_length,
               c.numeric_precision, c.numeric_scale, c.is_nullable
        FROM information_schema.columns c
        WHERE c.table_schema = {schema} AND c.table_name = {name}
        ORDER BY c.ordinal_position
    """

    pk_sql = """
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'PRIMARY KEY'
          AND tc.table_schema = {schema} AND tc.table_name = {name}
        ORDER BY kcu.ordinal_position
    """

    viewdef_sql = """
        SELECT pg_get_viewdef(c.oid, true)
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = {schema} AND c.relname = {name}
    """

    def fetch_rows(sql, params):
        cur.execute(sql, params)
        table = cur.fetch_arrow_table()
        return table.to_pylist()

    def fetch_columns(schema, name):
        rows = fetch_rows(
            col_sql.format(schema=_sql_literal(schema), name=_sql_literal(name)), ()
        )
        # Normalize information_schema column_name -> name to match the shape
        # expected by mssql_type() / generate_table_ddl().
        for row in rows:
            row["name"] = row.pop("column_name")
        return rows

    def fetch_pk(schema, name):
        rows = fetch_rows(
            pk_sql.format(schema=_sql_literal(schema), name=_sql_literal(name)), ()
        )
        return [r["column_name"] for r in rows]

    for kind, sql in (("table", table_sql), ("view", view_sql)):
        rows = fetch_rows(sql, ())
        for r in rows:
            schema = r["table_schema"]
            name = r["table_name"]
            columns = fetch_columns(schema, name)
            primary_keys = fetch_pk(schema, name)
            viewdef = None
            if kind == "view":
                vrows = fetch_rows(
                    viewdef_sql.format(
                        schema=_sql_literal(schema), name=_sql_literal(name)
                    ),
                    (),
                )
                viewdef = vrows[0]["pg_get_viewdef"] if vrows else None
            objects.append(Object(kind, schema, name, columns, primary_keys, viewdef))

    return objects


def export_table(conn, obj, outdir):
    """Export a table (or view result set) to a parquet file. Returns row count."""
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {obj.qualified}")
    path = outdir / obj.schema / f"{obj.name}.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    batchreader = cur.fetch_record_batch()
    row_count = 0
    with pq.ParquetWriter(path, batchreader.schema) as writer:
        try:
            while True:
                batch = batchreader.read_next_batch()
                writer.write(batch)
                row_count += batch.num_rows
        except StopIteration:
            pass
    return row_count, path


def mssql_type(col):
    """Return the MSSQL type string for a Postgres column dict, or raise."""
    data_type = (col["data_type"] or "").lower()
    entry = PG_TO_MSSQL.get(data_type)
    if entry is None:
        raise ValueError(
            f"Unsupported Postgres type '{col['data_type']}' for column '{col['name']}'"
        )
    mssql, needs_length, needs_ps = entry
    if needs_length:
        length = col["character_maximum_length"]
        if length is None or length <= 0 or length > 4000:
            # mssql-python maps >4000 to MAX; keep explicit for large text
            mssql = "NVARCHAR(MAX)" if "VARCHAR" in mssql or "CHAR" in mssql else mssql
        else:
            mssql = f"{mssql}({length})"
    elif needs_ps:
        precision = col["numeric_precision"] or 18
        scale = col["numeric_scale"] or 0
        mssql = f"{mssql}({precision},{scale})"
    return mssql


def generate_table_ddl(obj):
    lines = [f"CREATE TABLE {obj.mssql_object} ("]
    col_defs = []
    for col in obj.columns:
        nullable = "" if col["is_nullable"] == "NO" else " NULL"
        col_defs.append(f"    {quote_ident(col['name'])} {mssql_type(col)}{nullable}")
    if obj.primary_keys:
        pk = ", ".join(quote_ident(c) for c in obj.primary_keys)
        col_defs.append(f"    CONSTRAINT PK_{obj.name} PRIMARY KEY ({pk})")
    lines.append(",\n".join(col_defs))
    lines.append(");")
    return "\n".join(lines)


def translate_view_sql(sql, schema=None):
    """Best-effort convert a Postgres view definition to MSSQL syntax.

    Handles the constructs seen in the GES views:
      * `::type` casts are dropped (columns are passthroughs of native types).
      * double-quoted identifiers are converted to MSSQL brackets.
      * references qualified with the current release ``schema`` are dequalified
        to ``[table]``, since in MSSQL the view and its tables share the ``dbo``
        schema of the current database.
    More complex Postgres syntax (functions, window clauses, etc.) is out of
    scope and reported by the caller if the resulting SQL fails to execute.
    """

    # Drop Postgres ::<type> casts, e.g. `col::bigint` -> `col`. Postgres cast
    # type names are lowercase (possibly multi-word, e.g. `double precision`);
    # restricting to lowercase avoids eating the uppercase `AS`/keywords that
    # follow the cast.
    sql = re.sub(r"::\s*[a-z][a-z0-9_]*(\s+[a-z][a-z0-9_]*)*", "", sql)
    # Convert double-quoted identifiers to MSSQL brackets.
    sql = re.sub(r'"([^"]+)"', r"[\1]", sql)
    # Dequalify references to the current release schema (they live in dbo).
    # The schema may appear bracketed `[gesdr5].` (converted from `"gesdr5".`)
    # or as a bare identifier `gesdr5.` (as some pg_get_viewdef outputs do).
    if schema:
        schema = re.escape(schema)
        sql = re.sub(rf"(?:\[{schema}\]|{schema})\s*\.", "", sql)
    return sql


def generate_view_ddl(obj):
    if not obj.view_definition:
        raise ValueError(f"No view definition available for {obj.mssql_object}")
    body = translate_view_sql(obj.view_definition, obj.schema).rstrip().rstrip(";")
    return f"CREATE VIEW {obj.mssql_object} AS {body}"


def import_table(conn, obj, path):
    """Bulk-copy a parquet file into an MSSQL table. Returns row count."""
    cur = conn.cursor()
    result = cur.bulkcopy_arrow(obj.mssql_import_object, pq.ParquetFile(path).iter_batches())
    return result.get("rows_copied", 0)


def use_database(conn, database):
    """Switch the connection's current database context."""
    db_lit = database.replace("'", "''")
    conn.cursor().execute(f"USE [{db_lit}]")


def create_database(conn, database):
    """Create an MSSQL database for a data release (idempotent).

    With one database per data release, each Postgres schema becomes its own
    MSSQL database, and objects live in the default ``dbo`` schema.
    """
    db_lit = database.replace("'", "''")
    cur = conn.cursor()
    cur.execute(
        f"IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = '{db_lit}') "
        f"CREATE DATABASE [{db_lit}]"
    )
    print(f"  ensured database [{database}]")


def main():
    parser = argparse.ArgumentParser(
        description="Copy a PostgreSQL database to Microsoft SQL Server via parquet."
    )
    parser.add_argument("--postgres-url", help="ADBC Postgres connection URL (source).")
    parser.add_argument(
        "--mssql-conn",
        help="mssql-python connection string for the SQL Server instance, e.g. "
        "Server=mssql;Database=master;Uid=sa;Pwd=...;TrustServerCertificate=yes. "
        "Requires CREATE DATABASE permission when --create-databases is used. "
        "The initial database context is overridden per data release.",
    )
    parser.add_argument(
        "--schema", action="append", default=[],
        help="Postgres schema(s) to copy; each becomes a separate MSSQL database. "
        "Repeat for multiple. Default: all non-system schemas.",
    )
    parser.add_argument("--outdir", default="/tmp/pg2mssql", help="Parquet output directory.")
    parser.add_argument("--create-tables", action="store_true", help="Run DDL to create tables/views on MSSQL.")
    parser.add_argument("--drop-existing", action="store_true", help="DROP tables/views before creating.")
    parser.add_argument("--skip-export", action="store_true", help="Skip Postgres->parquet export.")
    parser.add_argument("--skip-import", action="store_true", help="Skip parquet->MSSQL import.")
    parser.add_argument("--only", action="append", default=[], help="Only process named objects (schema.name).")
    parser.add_argument(
        "--create-databases", action="store_true",
        help="Create one MSSQL database per data release (schema). Requires a "
        "connection with CREATE DATABASE permission (e.g. sa / master).",
    )
    args = parser.parse_args()

    if args.skip_export and args.skip_import:
        parser.error("--skip-export and --skip-import cannot both be set.")
    if args.skip_import and not args.mssql_conn:
        parser.error("--skip-import requires --mssql-conn.")
    if not args.skip_export and not args.postgres_url:
        parser.error("--postgres-url is required unless --skip-export is set.")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # ---- 1 + 2. Discover objects from Postgres, then export to parquet ----
    objects = []
    pg_conn = None
    if not args.skip_export:
        from adbc_driver_postgresql import dbapi as pgdb
        pg_conn = pgdb.connect(args.postgres_url)
        try:
            objects = discover(pg_conn, args.schema)
        except Exception:
            pg_conn.close()
            pg_conn = None
            raise
    else:
        # Re-discover requires Postgres; if skipping export we only import from
        # existing parquet files. Build the object list (with column metadata
        # read from each parquet file) so DDL/import still work.
        if args.schema:
            search = [Path(args.outdir) / s for s in args.schema]
        else:
            search = [Path(args.outdir)]
        for base in search:
            if not base.exists():
                continue
            for pf in base.rglob("*.parquet"):
                schema = pf.parent.name
                columns = [_column_from_arrow(f) for f in pq.ParquetFile(pf).schema_arrow]
                objects.append(Object("table", schema, pf.stem, columns, [], None))

    if args.only:
        wanted = set(args.only)
        objects = [o for o in objects
                   if (o.schema and f"{o.schema}.{o.name}" in wanted) or o.name in wanted]

    tables = [o for o in objects if o.kind == "table"]
    views = [o for o in objects if o.kind == "view"]
    print(f"Discovered {len(tables)} tables, {len(views)} views")

    # Export tables/views to parquet (pg_conn kept open from discovery).
    if not args.skip_export:
        print("Exporting Postgres -> parquet ...")
        for obj in objects:
            try:
                rows, path = export_table(pg_conn, obj, outdir)
                print(f"  exported {obj.qualified}: {rows} rows -> {path}")
            except Exception as exc:
                print(f"  ERROR exporting {obj.qualified}: {exc}", file=sys.stderr)
        pg_conn.close()

    # ---- 3 + 4. Generate DDL and import into MSSQL ----
    if not args.skip_import:
        import mssql_python
        # Connect to the SQL Server instance (login permissions needed for
        # CREATE DATABASE; the initial database context is irrelevant since we
        # USE <database> per data release below. Autocommit is required for
        # CREATE DATABASE (not allowed inside a transaction).
        ms_conn = mssql_python.connect(connection_str=args.mssql_conn, autocommit=True)
        try:
            databases = sorted({o.schema for o in objects if o.schema})
            if args.create_databases:
                print("Creating MSSQL databases (one per data release) ...")
                for db in databases:
                    create_database(ms_conn, db)

            if args.create_tables and args.drop_existing:
                print("Dropping existing tables/views ...")
                for obj in objects:
                    use_database(ms_conn, obj.schema)
                    dcur = ms_conn.cursor()
                    try:
                        dcur.execute(f"DROP {obj.kind.upper()} {obj.mssql_object}")
                    except Exception:
                        pass

            if args.create_tables:
                for obj in tables:
                    try:
                        use_database(ms_conn, obj.schema)
                        ms_conn.cursor().execute(generate_table_ddl(obj))
                        print(f"  created table {obj.mssql_object} in [{obj.schema}]")
                    except Exception as exc:
                        print(f"  ERROR creating table {obj.mssql_object}: {exc}", file=sys.stderr)

            for obj in tables:
                path = outdir / obj.schema / f"{obj.name}.parquet"
                if not path.exists():
                    print(f"  MISSING parquet for {obj.mssql_object}: {path}", file=sys.stderr)
                    continue
                try:
                    use_database(ms_conn, obj.schema)
                    rows = import_table(ms_conn, obj, path)
                    print(f"  imported {obj.mssql_object} in [{obj.schema}]: {rows} rows")
                except Exception as exc:
                    print(f"  ERROR importing {obj.mssql_object}: {exc}", file=sys.stderr)

            if args.create_tables:
                for obj in views:
                    try:
                        use_database(ms_conn, obj.schema)
                        ms_conn.cursor().execute(generate_view_ddl(obj))
                        print(f"  created view {obj.mssql_object} in [{obj.schema}]")
                    except Exception as exc:
                        print(f"  ERROR creating view {obj.mssql_object}: {exc}", file=sys.stderr)
        finally:
            ms_conn.close()

    print("Done.")


if __name__ == "__main__":
    main()