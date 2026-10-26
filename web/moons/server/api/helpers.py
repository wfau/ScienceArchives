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

def schema_view_schemas(access_type):
    schema_file = settings.QUERY_SCHEMA['SCHEMA_VIEW']
    return filter_schemas(schema_names(access_type), schema_file)

def validate_path(filename, schema=None):
    if not filename:
        return None
    base_str = settings.MOONS_DB['BASE_FILE_PATH'].get(schema)
    if not base_str:
        logger.error(f'No base file path for schema {schema}')
        return None
    base = Path(base_str).resolve(strict=False)
    # Normalise the *stored* path purely lexically (it is not a real filesystem
    # path yet), collapsing trailing slashes, repeated separators and '.', '..'.
    path = Path(filename).resolve(strict=False)
    if not path.is_relative_to(base):
        logger.error(f'Requested file path {filename} not relative to {base}')
        return None
    # Map to the real location, then re-check it stays inside /files/.
    mapped = Path('/files/').resolve(strict=False) / path.relative_to(base)
    if not mapped.is_relative_to(Path('/files/').resolve(strict=False)):
        logger.error(f'Resolved path {mapped} escaped /files/')
        return None
    return mapped

def has_perm_proprietary(user):
    return user.has_perm(settings.QUERY_DATABASE['PERMISSION_PROPRIETARY'])