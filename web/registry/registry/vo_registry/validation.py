from lxml.etree import _Element
from starlette.datastructures import QueryParams

from vo_registry.constants import MetadataFormats, QParams, SetSpecs, Verbs
from vo_registry.errors import (
    IdentifierNotFound,
    bad_arg,
    bad_resumption_token,
    bad_verb,
    cannot_disseminate_format,
    id_does_not_exist,
    no_records_match,
    no_set_hierarchy,
)
from vo_registry.resources import ResourceRepo
from vo_registry.utils import parse_datetime


REQUIRED_ARGS: dict[str, list[str]] = {
    Verbs.GET_RECORD: [QParams.IDENTIFIER, QParams.METADATA_PREFIX],
    Verbs.IDENTIFY: [],
    Verbs.LIST_IDENTIFIERS: [QParams.METADATA_PREFIX],
    Verbs.LIST_METADATA_FORMATS: [],
    Verbs.LIST_RECORDS: [QParams.METADATA_PREFIX],
    Verbs.LIST_SETS: [],
}


OPTIONAL_ARGS: dict[str, list[str]] = {
    Verbs.GET_RECORD: [],
    Verbs.IDENTIFY: [],
    Verbs.LIST_IDENTIFIERS: [
        QParams.FROM,
        QParams.UNTIL,
        QParams.SET,
        QParams.RESUMPTION_TOKEN,
    ],
    Verbs.LIST_METADATA_FORMATS: [QParams.IDENTIFIER],
    Verbs.LIST_RECORDS: [
        QParams.FROM,
        QParams.UNTIL,
        QParams.SET,
        QParams.RESUMPTION_TOKEN,
    ],
    Verbs.LIST_SETS: [QParams.RESUMPTION_TOKEN],
}

VALID_VERBS = list(Verbs)


def has_unknown_args(args: dict, total_args: list[str]) -> _Element | None:
    arg_keys = set(args.keys())
    if unknown_args := (arg_keys - set(total_args)):
        message = f"unknown query params: {unknown_args}"
        return bad_arg(message)
    return None


def is_missing_required_args(args: dict, required_args: list[str]) -> _Element | None:
    arg_keys = set(args.keys())
    if missing_keys := (set(required_args) - arg_keys):
        message = f"missing required query params: {missing_keys}"
        return bad_arg(message)
    return None


def unknown_identifier(repo: ResourceRepo, identifier: str) -> _Element | None:
    try:
        repo.get(identifier)
    except IdentifierNotFound:
        return id_does_not_exist(identifier)
    return None


def invalid_metadataprefix(mdp: str) -> _Element | None:
    if mdp not in set(MetadataFormats):
        return cannot_disseminate_format(mdp)
    return None


def invalid_setspec(setspec: str) -> _Element | None:
    if setspec != SetSpecs.IVO_MANAGED:
        return no_set_hierarchy(setspec)
    return None


def datetime_errors(datetime_str: str) -> _Element | None:
    try:
        parse_datetime(datetime_str)
    except ValueError:
        return bad_arg(f"invalid datetime format: {datetime_str}")
    return None


def from_until_errors(from_str: str, until_str: str) -> _Element | None:
    if len(from_str) != len(until_str):
        return bad_arg("datetime formats must have same granularity")
    from_datetime = parse_datetime(from_str)
    until_datetime = parse_datetime(until_str)
    if from_datetime > until_datetime:
        return bad_arg("from must be an earlier datetime than until")
    return None


def from_until_no_records(
    repo: ResourceRepo, from_str: str, until_str: str
) -> _Element | None:
    records = repo.get_all(from_str=from_str, until_str=until_str)
    if len(records) == 0:
        return no_records_match()
    return None


def check_from_records(repo: ResourceRepo, from_str: str) -> _Element | None:
    from_datetime = parse_datetime(from_str)
    if from_datetime > repo.latest_datetime:
        return no_records_match()
    return None


def check_until_records(repo: ResourceRepo, until_str: str) -> _Element | None:
    until_datetime = parse_datetime(until_str)
    if repo.earliest_datetime > until_datetime:
        return no_records_match()
    return None


def validate_query_params(
    query_params: QueryParams, repo: ResourceRepo
) -> list[_Element] | None:
    params = dict(query_params)
    verb = params.pop(QParams.VERB, None)
    if verb not in set(Verbs):
        return [bad_verb(verb)]
    keys = [k for k, v in query_params.multi_items()]
    if len(set(keys)) != len(keys):
        return [bad_arg("duplicate query parameters not allowed")]
    return validate_args(REQUIRED_ARGS[verb], OPTIONAL_ARGS[verb], params, repo)


def _qparam(input_args: dict, total_args: list[str], query_param: str) -> str | None:
    if (value := input_args.get(query_param)) and (query_param in total_args):
        return value
    return None


def validate_args(
    required_args: list[str],
    optional_args: list[str],
    input_args: dict,
    repo: ResourceRepo,
) -> list[_Element] | None:
    valid_datetimes = True
    total_args = required_args + optional_args
    errors = []

    errors.append(is_missing_required_args(input_args, required_args))

    errors.append(has_unknown_args(input_args, total_args))

    if identifier := _qparam(input_args, total_args, QParams.IDENTIFIER):
        errors.append(unknown_identifier(repo, identifier))

    if mdp := _qparam(input_args, total_args, QParams.METADATA_PREFIX):
        errors.append(invalid_metadataprefix(mdp))

    if setspec := _qparam(input_args, total_args, QParams.SET):
        errors.append(invalid_setspec(setspec))

    if _qparam(input_args, total_args, QParams.RESUMPTION_TOKEN):
        errors.append(bad_resumption_token())

    # etree.Element not truthy unless it has children
    if from_time := _qparam(input_args, total_args, QParams.FROM):
        from_err = datetime_errors(from_time)
        if from_err is not None:
            valid_datetimes = False
            errors.append(from_err)

    if until_time := _qparam(input_args, total_args, QParams.UNTIL):
        until_err = datetime_errors(until_time)
        if until_err is not None:
            valid_datetimes = False
            errors.append(until_err)

    if from_time and until_time and valid_datetimes:
        from_until_err = from_until_errors(from_time, until_time)
        if from_until_err is not None:
            errors.append(from_until_err)
        else:
            errors.append(from_until_no_records(repo, from_time, until_time))

    if until_time and valid_datetimes:
        errors.append(check_until_records(repo, until_time))

    if from_time and valid_datetimes:
        errors.append(check_from_records(repo, from_time))

    result = [e for e in errors if e is not None]
    if len(result) > 0:
        return result
    return None
