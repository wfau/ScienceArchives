from importlib import import_module
from pathlib import Path
import os

from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.utils import timezone
from django.utils.http import urlencode

from celery import shared_task

import pyarrow as pa
import pyarrow.parquet as pq
from astropy.table import Table

# import adbc_driver_postgresql.dbapi
# import adbc_driver_sqlite.dbapi

# db_url = 'file:///Users/amy/MOONS/development/mockdb/mock-gesiDR5.sqlite3'
# db_url = 'postgresql://postgres:12345@localhost:5432/'

# The query database may be an ADBC-backed store (SQLite, PostgreSQL) or
# Microsoft SQL Server. The backend is chosen per data release via
# settings.QUERY_DATABASE, defaulting to the global DRIVER:
#   * ADBC drivers are module paths, e.g. 'adbc_driver_sqlite.dbapi' or
#     'adbc_driver_postgresql.dbapi', and connect with a URL string.
#   * MSSQL uses the 'mssql' driver and connects with an mssql-python
#     connection string (e.g. 'Server=...;Database=...;Uid=...;Pwd=...').
MSSQL_DRIVER = 'mssql'


def _resolve_driver(schema=None):
    """Return the driver id for a schema.

    A schema may override the global driver via its entry in
    QUERY_DATABASE['CONNECTION_STRINGS'][schema]['driver']. Falls back to the
    global QUERY_DATABASE['DRIVER'].
    """
    if schema:
        entry = (settings.QUERY_DATABASE.get('CONNECTION_STRINGS', {}) or {}).get(schema)
        driver = (entry or {}).get('driver')
        if driver:
            return driver
    return settings.QUERY_DATABASE['DRIVER']


def _is_mssql(schema=None):
    return _resolve_driver(schema) == MSSQL_DRIVER


def _get_db_api(driver):
    if driver == MSSQL_DRIVER:
        from mssql_python import connect
        return connect
    return import_module(driver).connect


def _db_urls(schema=None):
    """Return (driver, proprietary, public) connection strings for a schema.

    Each data release (Postgres schema) maps to its own backend via
    QUERY_DATABASE['CONNECTION_STRINGS'][schema] = {driver?, proprietary, public}.
    Unmapped schemas fall back to the global driver and CONNECTION_STRING* values.
    """
    driver = _resolve_driver(schema)
    default = (
        settings.QUERY_DATABASE['CONNECTION_STRING'],
        settings.QUERY_DATABASE['CONNECTION_STRING_PUBLIC'],
    )
    if not schema:
        return driver, default[0], default[1]
    entry = (settings.QUERY_DATABASE.get('CONNECTION_STRINGS', {}) or {}).get(schema)
    if not entry:
        return driver, default[0], default[1]
    return (
        driver,
        entry.get('proprietary') or default[0],
        entry.get('public') or default[1],
    )


class _MssqlCursor:
    """Wraps an mssql-python cursor so it exposes the same record-batch
    interface as an ADBC cursor (``fetch_record_batch()``)."""

    def __init__(self, cursor, batch_size=None):
        self._cursor = cursor
        self._batch_size = batch_size or settings.QUERY_DATABASE.get('BATCH_SIZE')

    def execute(self, query):
        return self._cursor.execute(query)

    def fetch_record_batch(self):
        return self._cursor.arrow_reader(batch_size=self._batch_size)

    def fetch_arrow_table(self):
        return self._cursor.arrow(batch_size=self._batch_size)

    def close(self):
        return self._cursor.close()


def get_connection(url, schema=None, timeout=None):
    """Return a connection whose cursor exposes ``execute``, ``fetch_record_batch``
    and ``fetch_arrow_table`` regardless of the underlying backend.

    ``timeout`` (seconds, MSSQL only) is applied as the per-statement query
    timeout so long queries are halted rather than running unbounded.
    """
    driver = _resolve_driver(schema)
    connect = _get_db_api(driver)
    if driver == MSSQL_DRIVER:
        # Queries are always SELECT against a read-only user, so run them in
        # autocommit mode. With autocommit off mssql-python holds the
        # server-side cursor, its locks and tempdb resources open for the whole
        # streaming read, which adds latency and memory pressure.
        conn = connect(connection_str=url, autocommit=True)
        if timeout:
            # Per-statement query timeout (SQL_ATTR_QUERY_TIMEOUT); 0 = wait
            # indefinitely. Must be set before any cursor is created from it.
            conn.timeout = timeout
        return conn
    return connect(url)

from .models import ExecuteSQL

import logging
logger = logging.getLogger(__name__)

def write_results(cursor, output_file):
    count = 0
    row_count = 0
    # with pa.OSFile(output_file, 'wb') as sink:
    batchreader = cursor.fetch_record_batch()
    with pq.ParquetWriter(output_file, batchreader.schema) as writer:
        try:
            while True:
                batch = batchreader.read_next_batch()
                writer.write(batch)
                row_count += batch.num_rows
                count += 1
        except StopIteration:
            # finished
            pass
    logger.info(f'Wrote {count} batch(es) to {output_file}')
    return row_count

def read_table(input_file):
    return Table.read(input_file)

def to_json(schema):
    result = []
    for n,t in zip(schema.names, schema.types):
        if t == pa.int64():
            type_name = 'bigint'
        elif t == pa.int32():
            type_name = 'int'
        elif t == pa.int16():
            type_name = 'smallint'
        elif t == pa.int8():
            type_name = 'tinyint'
        elif t == pa.float32():
            type_name = 'float'
        elif t == pa.float64():
            type_name = 'double'
        result.append([n, type_name])
    return result

def get_db_url(user, schema):
    db_url, db_public_url = _db_urls(schema)[1:]
    if user.has_perm(settings.QUERY_DATABASE['PERMISSION_PROPRIETARY']):
        url = db_url
    else:
        url = db_public_url
    if schema and not _is_mssql(schema):
        # this is PostgreSQL specific
        options = urlencode({'options': f'--search_path={schema}'})
        url = f'{url}?{options}'
    return url

@shared_task
def execute(exec_pk):
    job = ExecuteSQL.objects.get(pk=exec_pk)
    job.started = timezone.now()
    job.status = ExecuteSQL.StatusType.RUNNING
    results_file = os.path.join(settings.LOCAL_FILE_DIR, f'{job.pk}.parquet')
    job.save()
    conn = None
    cursor = None
    start = timezone.now()
    try:
        url = get_db_url(job.user, job.schema)
        conn = get_connection(url, job.schema, timeout=job.timeout)
        cursor = conn.cursor()
        if _is_mssql(job.schema):
            cursor = _MssqlCursor(cursor)
        cursor.execute(job.query)
        row_count = write_results(cursor, results_file)
        # print(f'row count: {row_count}')
        job.num_rows = row_count
        job.results_file = results_file
    except Exception as exc:
        import traceback
        traceback.print_exc()
        job.results_error = str(exc)
    finally:
        # Always release the DB resources, even on error. For MSSQL this closes
        # the server-side cursor and releases its locks and tempdb.
        for resource in (cursor, conn):
            try:
                resource.close()
            except Exception:
                pass
        # print('job completed')
        # print(f'has error? {job.results_error}')
        job.completed = timezone.now()
        job.status = ExecuteSQL.StatusType.COMPLETED
        job.save()
        logger.info(
            f"Query {job.pk} schema={job.schema} rows={job.num_rows} "
            f"outcome={job.current_status} "
            f"took {(job.completed - start).total_seconds():.2f}s"
        )

def execute_sync(user, query, schema=None):
    '''
    Synchronous SQL query
    Use with caution - small resultsets only.

    This is used to provide the metadata for the target page
    which only contains one or two rows.
    '''
    url = get_db_url(user, schema)
    conn = None
    cursor = None
    try:
        conn = get_connection(url, schema)
        cursor = conn.cursor()
        if _is_mssql(schema):
            cursor = _MssqlCursor(cursor)
        cursor.execute(query)
        return cursor.fetch_arrow_table()
    finally:
        for resource in (cursor, conn):
            try:
                resource.close()
            except Exception:
                pass

@shared_task
def remove_results(hours=0, days=0):
    if not hours and not days:
        logger.info('Did not specify days or hours: No files to remove')
        return
    deleted_files = 0
    max_age = timezone.now() - relativedelta(hours=hours, days=days)
    for query in ExecuteSQL.objects.filter(completed__lte=max_age):
        if query.results_file:
            try:
                path = Path(query.results_file)
                logger.info(f'Removing results file "{path.name}" generated {query.completed}')
                path.unlink(missing_ok=True)
                query.results_file = None
                query.save()
                deleted_files += 1
            except:
                logger.error(f'Error removing results file "{path.name}"')
    logger.info(f'Deleted {deleted_files} query results files generated before {max_age}')
