from datetime import datetime
from unittest.mock import patch

from starlette.datastructures import QueryParams

from vo_registry.constants import Errors, OAI_NS, QParams, MetadataFormats, Verbs
from vo_registry.validation import (
    check_from_records,
    check_until_records,
    datetime_errors,
    has_unknown_args,
    invalid_metadataprefix,
    invalid_setspec,
    is_missing_required_args,
    unknown_identifier,
    validate_args,
    validate_query_params,
)


def assert_error_elem(result, error):
    assert len(result) == 1
    assert result[0].tag == f"{{{OAI_NS}}}error"
    assert result[0].items() == [("code", error)]


@patch("vo_registry.validation.validate_args", autospec=True)
class TestValidateQueryParams:
    def test_unknown_verb(self, mock_validate, test_repo):
        query_params = QueryParams([(QParams.VERB, "NotAVerb")])
        result = validate_query_params(query_params, test_repo)
        mock_validate.assert_not_called()
        assert_error_elem(result, Errors.BAD_VERB)

    def test_duplicate_query_params(self, mock_validate, test_repo):
        query_params = QueryParams(
            [
                (QParams.VERB, Verbs.LIST_IDENTIFIERS),
                (QParams.METADATA_PREFIX, MetadataFormats.OAI_DC),
                (QParams.METADATA_PREFIX, MetadataFormats.OAI_DC),
            ]
        )
        result = validate_query_params(query_params, test_repo)
        mock_validate.assert_not_called()
        assert_error_elem(result, Errors.BAD_ARGUMENT)

    def test_valid_args(self, mock_validate, test_repo):
        query_params = QueryParams(
            [
                (QParams.VERB, Verbs.LIST_IDENTIFIERS),
                (QParams.METADATA_PREFIX, MetadataFormats.OAI_DC),
            ]
        )
        validate_query_params(query_params, test_repo)
        mock_validate.assert_called_once()


class TestValidateArgs:
    def test_returns_none_when_required_args_present(self, test_repo):
        input_args = {QParams.METADATA_PREFIX: MetadataFormats.IVO_VOR}
        result = validate_args([QParams.METADATA_PREFIX], [], input_args, test_repo)
        assert result is None

    def test_returns_none_when_total_args_present(self, test_repo):
        input_args = {
            QParams.METADATA_PREFIX: MetadataFormats.IVO_VOR,
            QParams.IDENTIFIER: test_repo.registry_id,
        }
        result = validate_args(
            [QParams.METADATA_PREFIX], [QParams.IDENTIFIER], input_args, test_repo
        )
        assert result is None

    def test_missing_a_required_arg(self, test_repo):
        input_args = {QParams.METADATA_PREFIX: MetadataFormats.IVO_VOR}
        result = validate_args(
            [QParams.METADATA_PREFIX, QParams.FROM], [], input_args, test_repo
        )
        assert_error_elem(result, Errors.BAD_ARGUMENT)

    def test_has_unnecessary_arg(self, test_repo):
        input_args = {
            QParams.METADATA_PREFIX: MetadataFormats.IVO_VOR,
            QParams.IDENTIFIER: test_repo.registry_id,
        }
        result = validate_args([QParams.METADATA_PREFIX], [], input_args, test_repo)
        assert_error_elem(result, Errors.BAD_ARGUMENT)

    def test_has_unknown_identifier(self, test_repo):
        input_args = {QParams.IDENTIFIER: "not_a_real_id"}
        result = validate_args([QParams.IDENTIFIER], [], input_args, test_repo)
        assert_error_elem(result, Errors.ID_DOES_NOT_EXIST)

    def test_has_unknown_mdp(self, test_repo):
        input_args = {QParams.METADATA_PREFIX: "not_a_real_mdp"}
        result = validate_args([QParams.METADATA_PREFIX], [], input_args, test_repo)
        assert_error_elem(result, Errors.CANNOT_DISSEMINATE_FORMAT)

    # I don't think this follows the OAI-PMH spec
    # noSetHierarchy is for when the registry doesn't support sets,
    # not for when no records are found
    # I think this should be simply noRecordsMatch
    def test_has_unknown_setspec(self, test_repo):
        input_args = {QParams.SET: "not_a_real_set"}
        result = validate_args([QParams.SET], [], input_args, test_repo)
        assert_error_elem(result, Errors.NO_SET_HIERARCHY)

    def test_has_known_setspec(self, test_repo):
        input_args = {QParams.SET: "ivo_managed"}
        result = validate_args([QParams.SET], [], input_args, test_repo)
        assert result is None

    # At this time, the registry doesn't support pagination
    def test_has_resumption_token(self, test_repo):
        input_args = {QParams.RESUMPTION_TOKEN: "not_a_real_token"}
        result = validate_args([], [QParams.RESUMPTION_TOKEN], input_args, test_repo)
        assert_error_elem(result, Errors.BAD_RESUMPTION_TOKEN)

    def test_from_and_until_valid_datetime_string(self, test_repo):
        input_args = {
            QParams.FROM: "2024-01-25T17:12:48Z",
            QParams.UNTIL: "2025-01-25T17:12:48Z",
        }
        result = validate_args([], [QParams.FROM, QParams.UNTIL], input_args, test_repo)
        assert result is None

    def test_from_and_until_valid_but_no_records(self, test_repo):
        input_args = {
            QParams.FROM: "2024-01-25T17:12:48Z",
            QParams.UNTIL: "2024-01-25T17:12:50Z",
        }
        result = validate_args([], [QParams.FROM, QParams.UNTIL], input_args, test_repo)
        assert_error_elem(result, Errors.NO_RECORDS_MATCH)

    def test_from_valid_datetime_string(self, test_repo):
        input_args = {QParams.FROM: "2024-01-25T17:12:48Z"}
        result = validate_args([], [QParams.FROM], input_args, test_repo)
        assert result is None

    def test_from_invalid_date(self, test_repo):
        input_args = {QParams.FROM: "2023-23-12"}
        result = validate_args([], [QParams.FROM], input_args, test_repo)
        assert_error_elem(result, Errors.BAD_ARGUMENT)

    def test_from_invalid_format(self, test_repo):
        input_args = {QParams.FROM: str(datetime(2023, 2, 12, 14, 29, 32, 930849))}
        result = validate_args([], [QParams.FROM], input_args, test_repo)
        assert_error_elem(result, Errors.BAD_ARGUMENT)

    def test_until_valid_datetime_string(self, test_repo):
        input_args = {QParams.UNTIL: "2024-03-25T17:12:48Z"}
        result = validate_args([], [QParams.UNTIL], input_args, test_repo)
        assert result is None

    def test_until_invalid_date(self, test_repo):
        input_args = {QParams.UNTIL: "2023-23-12"}
        result = validate_args([], [QParams.UNTIL], input_args, test_repo)
        assert_error_elem(result, Errors.BAD_ARGUMENT)

    def test_until_invalid_format(self, test_repo):
        input_args = {QParams.UNTIL: str(datetime(2023, 2, 12, 14, 29, 32, 930849))}
        result = validate_args([], [QParams.UNTIL], input_args, test_repo)
        assert_error_elem(result, Errors.BAD_ARGUMENT)

    def test_valid_from_until(self, test_repo):
        input_args = {
            QParams.FROM: "2024-02-01T17:12:48Z",
            QParams.UNTIL: "2024-03-25T17:12:48Z",
        }
        result = validate_args([], [QParams.FROM, QParams.UNTIL], input_args, test_repo)
        assert result is None

    def test_from_until_different_granularity(self, test_repo):
        input_args = {QParams.FROM: "2024-02-01", QParams.UNTIL: "2024-03-25T17:12:48Z"}
        result = validate_args([], [QParams.FROM, QParams.UNTIL], input_args, test_repo)
        assert_error_elem(result, Errors.BAD_ARGUMENT)

    def test_from_after_until(self, test_repo):
        input_args = {QParams.FROM: "2024-02-01", QParams.UNTIL: "2024-01-25"}
        result = validate_args([], [QParams.FROM, QParams.UNTIL], input_args, test_repo)
        assert_error_elem(result, Errors.BAD_ARGUMENT)

    def test_from_and_until_are_both_invalid(self, test_repo):
        input_args = {QParams.FROM: "2024-70-01", QParams.UNTIL: "2024-01-25-abc"}
        result = validate_args([], [QParams.FROM, QParams.UNTIL], input_args, test_repo)
        assert len(result) == 2
        assert result[0].tag == f"{{{OAI_NS}}}error"
        assert result[0].items() == [("code", Errors.BAD_ARGUMENT)]

    def test_until_before_ealiest(self, test_repo):
        input_args = {QParams.UNTIL: "1983-11-12"}
        result = validate_args([], [QParams.UNTIL], input_args, test_repo)
        assert len(result) == 1
        assert result[0].tag == f"{{{OAI_NS}}}error"
        assert result[0].items() == [("code", Errors.NO_RECORDS_MATCH)]

    def test_from_after_latest(self, test_repo):
        input_args = {
            QParams.FROM: datetime.utcnow().isoformat(timespec="seconds") + "Z"
        }
        result = validate_args([], [QParams.FROM], input_args, test_repo)
        assert len(result) == 1
        assert result[0].tag == f"{{{OAI_NS}}}error"
        assert result[0].items() == [("code", Errors.NO_RECORDS_MATCH)]


class TestCheckForUnknownArgs:
    def test_returns_unknown_args(self):
        optional_args = ["aaa", "ccc"]
        args = {"aaa": 1, "bbb": 2, "ccc": 3}
        result = has_unknown_args(args, optional_args)
        assert result.tag == f"{{{OAI_NS}}}error"
        assert result.items() == [("code", Errors.BAD_ARGUMENT)]
        assert "bbb" in result.text

    def test_returns_none_if_no_unknown_args(self):
        optional_args = ["a", "c"]
        args = {"a": 1}
        invalid_args = has_unknown_args(args, optional_args)
        assert invalid_args is None


class TestUnknownIdentifier:
    def test_returns_unknown_id(self, test_repo):
        result = unknown_identifier(test_repo, "bad_id")
        assert result.tag == f"{{{OAI_NS}}}error"
        assert result.items() == [("code", Errors.ID_DOES_NOT_EXIST)]
        assert "bad_id" in result.text

    def test_returns_none_if_id_known(self, test_repo):
        result = unknown_identifier(test_repo, test_repo.registry_id)
        assert result is None


class TestIsMissingRequiredArgs:
    def test_returns_missing_args(self):
        required_args = ["aaa", "bbb", "ccc"]
        args = {"bbb": 3}
        result = is_missing_required_args(args, required_args)
        assert result.tag == f"{{{OAI_NS}}}error"
        assert result.items() == [("code", Errors.BAD_ARGUMENT)]
        assert "aaa" in result.text
        assert "ccc" in result.text

    def test_returns_none_when_no_missing_args(self):
        required_args = ["a", "b", "c"]
        args = {"b": 3, "a": 1, "c": 5, "d": 7}
        result = is_missing_required_args(args, required_args)
        assert result is None


class TestInvalidMetadataPrefix:
    def test_returns_invalid_mdp(self):
        result = invalid_metadataprefix("not_a_real_mdp")
        assert result.tag == f"{{{OAI_NS}}}error"
        assert result.items() == [("code", Errors.CANNOT_DISSEMINATE_FORMAT)]
        assert "not_a_real_mdp" in result.text

    def test_returns_none_when_valid_mdp(self):
        result = invalid_metadataprefix(MetadataFormats.IVO_VOR)
        assert result is None


class TestInvalidSetSpec:
    def test_returns_invalid_setspec(self):
        result = invalid_setspec("not_a_real_set")
        assert result.tag == f"{{{OAI_NS}}}error"
        assert result.items() == [("code", Errors.NO_SET_HIERARCHY)]
        assert "not_a_real_set" in result.text

    def test_returns_none_when_valid_setspec(self):
        result = invalid_setspec("ivo_managed")
        assert result is None


class TestDatetimeErrors:
    def test_valid_date(self):
        result = datetime_errors("2024-03-25")
        assert result is None

    def test_valid_datetime(self):
        result = datetime_errors("2024-03-25T17:12:48Z")
        assert result is None

    def test_unparsable_datetime_string(self):
        result = datetime_errors("2024-02-12 13:49:37.305429")
        assert result.tag == f"{{{OAI_NS}}}error"
        assert result.items() == [("code", Errors.BAD_ARGUMENT)]
        assert "2024-02-12 13:49:37.305429" in result.text


class TestCheckUntilRecords:
    def test_valid_date(self, test_repo):
        result = check_until_records(test_repo, "2024-02-02")
        assert result is None

    def test_invalid_date(self, test_repo):
        result = check_until_records(test_repo, "1853-02-02")
        assert result.tag == f"{{{OAI_NS}}}error"
        assert result.items() == [("code", Errors.NO_RECORDS_MATCH)]


class TestCheckFromRecords:
    def test_valid_date(self, test_repo):
        result = check_from_records(test_repo, "2020-02-02")
        assert result is None

    def test_invalid_date(self, test_repo):
        result = check_from_records(test_repo, "2130-02-02")
        assert result.tag == f"{{{OAI_NS}}}error"
        assert result.items() == [("code", Errors.NO_RECORDS_MATCH)]
