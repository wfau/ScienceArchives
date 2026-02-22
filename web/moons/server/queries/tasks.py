from importlib import import_module
import os

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

db_api = import_module(settings.QUERY_DATABASE['DRIVER'])
db_url = settings.QUERY_DATABASE['CONNECTION_STRING']
db_public_url = settings.QUERY_DATABASE['CONNECTION_STRING_PUBLIC']

from .models import ExecuteSQL

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
    print(f'Wrote {count} batch(es) to {output_file}', flush=True)
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
    if user.has_perm('queries.view_execute_sql'):
        url = db_url
    else:
        url = db_public_url
    if schema:
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
    try:
        url = get_db_url(job.user, job.schema)
        conn = db_api.connect(url)
        cursor = conn.cursor()
        cursor.execute(job.query)
        row_count = write_results(cursor, results_file)
        # print(f'row count: {row_count}')
        job.num_rows = row_count
        cursor.close()
        conn.close()
        job.results_file = results_file
    except Exception as exc:
        import traceback
        traceback.print_exc()
        job.results_error = str(exc)
    finally:
        # print('job completed')
        # print(f'has error? {job.results_error}')
        # job.completed = timezone.now()
        job.status = ExecuteSQL.StatusType.COMPLETED
        job.save()

def execute_sync(user, query, schema=None):
    '''
    Synchronous SQL query
    Use with caution - small resultsets only.

    This is used to provide the metadata for the target page
    which only contains one or two rows.
    '''
    url = get_db_url(user, schema)
    conn = db_api.connect(url)
    cursor = conn.cursor()
    cursor.execute(query)
    table = cursor.fetch_arrow_table()
    cursor.close()
    conn.close()
    return table
