import json
from pathlib import Path

from django.conf import settings

from queries.models import QueryPermissions

import logging
logger = logging.getLogger(__name__)

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

def validate_path(filename):
    if not filename:
        return None
    base = Path(settings.MOONS_DB['BASE_FILE_PATH'])
    local_base = Path('/files/')
    path = Path(filename)
    if not path.is_relative_to(base):
        logger.error(f'Requested file path {filename} not relative to {base}')
        return None
    return local_base / path.relative_to(base)

def has_perm_proprietary(user):
    return user.has_perm(settings.QUERY_DATABASE['PERMISSION_PROPRIETARY'])