from lxml import etree
from lxml.etree import _Element

from vo_registry.constants import Errors, OAI_NS, SetSpecs, MetadataFormats, Verbs


class IdentifierNotFound(Exception):
    pass


def _make_error_element(error: Errors, message: str) -> _Element:
    root = etree.Element(f"{{{OAI_NS}}}error")
    root.set("code", error)
    root.text = message
    return root


def bad_verb(verb: str | None) -> _Element:
    msg = f"{verb} is not a valid verb. Valid options are {[str(v) for v in Verbs]}"
    return _make_error_element(Errors.BAD_VERB, msg)


def bad_arg(msg: str) -> _Element:
    return _make_error_element(Errors.BAD_ARGUMENT, msg)


def id_does_not_exist(identifier: str) -> _Element:
    msg = f"identifier {identifier} not found"
    return _make_error_element(Errors.ID_DOES_NOT_EXIST, msg)


def cannot_disseminate_format(mdf: str) -> _Element:
    msg = (
        f"{mdf} is an unknown metadataPrefix, valid options are "
        f"{[str(m) for m in MetadataFormats]}"
    )
    return _make_error_element(Errors.CANNOT_DISSEMINATE_FORMAT, msg)


def no_set_hierarchy(setspec: str) -> _Element:
    msg = f"{setspec} is invalid, valid sets are {[str(s) for s in SetSpecs]}"
    return _make_error_element(Errors.NO_SET_HIERARCHY, msg)


def bad_resumption_token() -> _Element:
    msg = "registry does not support resumption"
    return _make_error_element(Errors.BAD_RESUMPTION_TOKEN, msg)


def no_records_match() -> _Element:
    msg = "no records in time selected"
    return _make_error_element(Errors.NO_RECORDS_MATCH, msg)
