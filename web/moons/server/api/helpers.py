import json

from django.conf import settings

from queries.models import QueryPermissions

def schema_names(access_type):
    return [perm.schema for perm in QueryPermissions.objects.filter(access=access_type)]

def filter_schemas(permitted_names, schema_file):
    with open(schema_file) as f:
        table_schema = json.load(f)
    return {k: v for k,v in table_schema.items() if k in permitted_names}

def query_view_schemas(access_type):
    schema_file = settings.QUERY_SCHEMA['QUERY_VIEW']
    return filter_schemas(schema_names(access_type), schema_file)

def schema_view_schemas(access_type):
    schema_file = settings.QUERY_SCHEMA['SCHEMA_VIEW']
    return filter_schemas(schema_names(access_type), schema_file)
