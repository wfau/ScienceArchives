from vo_registry.constants import Errors, OAI_NS
from vo_registry.errors import (
    bad_arg,
    bad_resumption_token,
    bad_verb,
    cannot_disseminate_format,
    id_does_not_exist,
    no_records_match,
    no_set_hierarchy,
)


class TestBadVerb:
    def test_return_error_element(self):
        result = bad_verb("IllegalVerb")
        assert result.tag == f"{{{OAI_NS}}}error"
        assert result.items() == [("code", Errors.BAD_VERB)]
        assert "IllegalVerb" in result.text


class TestBadArg:
    def test_return_error_element(self):
        result = bad_arg("test msg")
        assert result.tag == f"{{{OAI_NS}}}error"
        assert result.items() == [("code", Errors.BAD_ARGUMENT)]
        assert result.text == "test msg"


class TestIdDoesNotExist:
    def test_return_error_element(self):
        result = id_does_not_exist("someID")
        assert result.tag == f"{{{OAI_NS}}}error"
        assert result.items() == [("code", Errors.ID_DOES_NOT_EXIST)]
        assert "someID" in result.text


class TestCannotDisseminateFormat:
    def test_return_error_element(self):
        result = cannot_disseminate_format("bad_format")
        assert result.tag == f"{{{OAI_NS}}}error"
        assert result.items() == [("code", Errors.CANNOT_DISSEMINATE_FORMAT)]
        assert "bad_format" in result.text


class TestNoSetHeirarchy:
    def test_return_error_element(self):
        result = no_set_hierarchy("some_set")
        assert result.tag == f"{{{OAI_NS}}}error"
        assert result.items() == [("code", Errors.NO_SET_HIERARCHY)]
        assert "some_set" in result.text


class TestBadResumptionToken:
    def test_return_error_element(self):
        result = bad_resumption_token()
        assert result.tag == f"{{{OAI_NS}}}error"
        assert result.items() == [("code", Errors.BAD_RESUMPTION_TOKEN)]
        assert result.text == "registry does not support resumption"


class TestNoRecordsMatch:
    def test_return_error_element(self):
        result = no_records_match()
        assert result.tag == f"{{{OAI_NS}}}error"
        assert result.items() == [("code", Errors.NO_RECORDS_MATCH)]
        assert result.text == "no records in time selected"
