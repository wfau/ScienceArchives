from django.utils import timezone

from celery import shared_task

import pyarrow as pa
# import adbc_driver_postgresql.dbapi
import adbc_driver_sqlite.dbapi

db_url = 'file:///Users/amy/MOONS/development/mockdb/mock-gesiDR5.sqlite3'
# db_url = 'postgresql://postgres:12345@localhost:5432/'

from .models import ExecuteSQL

def write_results(cursor, output_file):
    count = 0
    with pa.OSFile(output_file, 'wb') as sink:
        batchreader = cursor.fetch_record_batch()
        with pa.ipc.new_file(sink, batchreader.schema) as writer:
            try:
                while True:
                    batch = batchreader.read_next_batch()
                    writer.write(batch)
                    count += 1
            except StopIteration:
                # finished
                pass
    print(f'Wrote {count} batch(es) to {output_file}')
    return count

def read_table(input_file):
    with pa.OSFile(input_file, 'rb') as source:
        return pa.ipc.open_file(source).read_all()

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

@shared_task
def execute(exec_pk):
    job = ExecuteSQL.objects.get(pk=exec_pk)
    job.started = timezone.now()
    job.status = ExecuteSQL.StatusType.RUNNING
    results_file = f'/Users/amy/MOONS/development/MOONS-web/moons-django/files/{job.pk}.arrow'
    job.save()
    try:
        # conn = adbc_driver_postgresql.dbapi.connect(db_url)
        conn = adbc_driver_sqlite.dbapi.connect(db_url)
        cursor = conn.cursor()
        cursor.execute(job.query)
        write_results(cursor, results_file)
        cursor.close()
        conn.close()
        job.results_file = results_file
    except Exception as exc:
        import traceback
        traceback.print_exc()
        job.results_error = str(exc)
    finally:
        job.completed = timezone.now()
        job.status = ExecuteSQL.StatusType.COMPLETED
        job.save()

# conn = adbc_driver_sqlite.dbapi.connect(db_url)
# cursor = conn.cursor()
# cursor.execute('SELECT rv FROM Spectrum LIMIT 10')
# # write_results(cursor, 'Spectrum.rv.arrow')
# i = 0
# with pa.OSFile('Spectrum.rv.arrow', 'wb') as sink:
#     batchreader = cursor.fetch_record_batch()
#     with pa.ipc.new_file(sink, batchreader.schema) as writer:
#         try:
#             while True:
#                 batch = batchreader.read_next_batch()
#                 writer.write(batch)
#                 i += batch.num_rows
#         except StopIteration:
#             # finished
#             pass
# print(f'num rows: {i}')
# cursor.close()
# conn.close()

# read_table('Spectrum.rv.arrow')
