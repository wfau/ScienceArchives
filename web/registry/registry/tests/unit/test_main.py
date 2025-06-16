from functools import lru_cache
from unittest.mock import patch
from urllib.robotparser import RobotFileParser

from fastapi.testclient import TestClient
from lxml import etree
from starlette.datastructures import QueryParams

from vo_registry import main
from vo_registry.constants import QParams, Verbs
from vo_registry.main import get_resource_repo

VERB_ELEM = etree.Element("Verb")
ERROR_ELEM = etree.Element("Error")
OAI_ELEM = etree.Element("OAI-PMH").getroottree()


class FakeRepo:
    pass


@lru_cache
def get_test_repo():
    return FakeRepo()


client = TestClient(main.app)
main.app.dependency_overrides[get_resource_repo] = get_test_repo


@patch("vo_registry.main.ResourceRepo")
class TestGetResourceRepo:
    def test_returns_resource_repo(self, mock_repo):
        repo = main.get_resource_repo()
        assert repo == mock_repo.return_value

    def test_caches_repo(self, mock_repo):
        main.get_resource_repo.cache_clear()
        main.get_resource_repo()
        main.get_resource_repo()
        mock_repo.assert_called_once()


class TestHelloWorld:
    def test_hello_world(self):
        response = client.get("/")
        assert response.status_code == 200


class TestFavicon:
    def test_get_favicon(self):
        response = client.get("/favicon.ico")
        assert response.status_code == 200


class TestRobots:
    def test_read_robots_txt(self):
        response = client.get("/robots.txt")
        assert response.status_code == 200
        rfp = RobotFileParser()
        rfp.parse(response.text.splitlines())
        assert rfp.can_fetch("*", "/index.html")
        assert not rfp.can_fetch("*", "/registry")


@patch("vo_registry.main.validate_query_params", return_value=None, autospec=True)
@patch("vo_registry.main.bad_verb", return_value=VERB_ELEM, autospec=True)
@patch("vo_registry.main.oai_wrap", return_value=OAI_ELEM, autospec=True)
class TestUnreachableUnknownVerbSelection:
    def test_unknown_verb_call_bad_verb(self, mock_oai_wrap, mock_bad_verb, mock_v):
        params = {QParams.VERB: "IllegalVerb"}
        client.get("/registry", params=params)
        mock_bad_verb.assert_called_once_with("IllegalVerb")
        mock_oai_wrap.assert_called_once_with(
            [mock_bad_verb.return_value],
            QueryParams({QParams.VERB: "IllegalVerb"}),
            "http://testserver/registry",
        )


@patch("vo_registry.main.validate_query_params", autospec=True)
@patch("vo_registry.main.oai_wrap", return_value=OAI_ELEM, autospec=True)
class TestValidateFails:
    def test_validate_returns_errors(self, mock_oai_wrap, mock_validate):
        mock_validate.return_value = [VERB_ELEM]
        params = {QParams.VERB: "IllegalVerb"}
        client.get("/registry", params=params)
        mock_oai_wrap.assert_called_once_with(
            mock_validate.return_value,
            QueryParams({QParams.VERB: "IllegalVerb"}),
            "http://testserver/registry",
        )


@patch("vo_registry.main.validate_query_params", return_value=None, autospec=True)
@patch("vo_registry.main.identify", return_value=[VERB_ELEM], autospec=True)
@patch("vo_registry.main.oai_wrap", return_value=OAI_ELEM, autospec=True)
class TestRequestURL:
    def test_with_x_forwarded_proto(self, mock_oai_wrap, mock_identify, mock_validate):
        params = {QParams.VERB: Verbs.IDENTIFY}
        client.get("/registry", params=params, headers={"X-Forwarded-Proto": "https"})
        mock_oai_wrap.assert_called_once_with(
            mock_identify.return_value,
            QueryParams({QParams.VERB: Verbs.IDENTIFY}),
            "https://testserver/registry",
        )

    def test_without_x_forwarded_proto(
        self, mock_oai_wrap, mock_identify, mock_validate
    ):
        params = {QParams.VERB: Verbs.IDENTIFY}
        client.get("/registry", params=params)
        mock_oai_wrap.assert_called_once_with(
            mock_identify.return_value,
            QueryParams({QParams.VERB: Verbs.IDENTIFY}),
            "http://testserver/registry",
        )


class VerbSelectionBase:
    VERB = "verb"
    PATH = "/registry"

    def test_get_returns_200(self, mock_oai_wrap, mock_verb, mock_validate):
        response = client.get(self.PATH, params={QParams.VERB: self.VERB})
        assert response.status_code == 200

    def test_post_returns_200(self, mock_oai_wrap, mock_verb, mock_validate):
        response = client.post(self.PATH, params={QParams.VERB: self.VERB})
        assert response.status_code == 200

    def test_calls_verb(self, mock_oai_wrap, mock_verb, mock_validate):
        client.get(self.PATH, params={QParams.VERB: self.VERB})
        mock_verb.assert_called_once()

    def test_invalid_params(self, mock_oai_wrap, mock_verb, mock_validate):
        mock_validate.return_value = [ERROR_ELEM]
        client.get(self.PATH, params={QParams.VERB: self.VERB})
        mock_verb.assert_not_called()
        mock_oai_wrap.assert_called_once_with(
            mock_validate.return_value,
            QueryParams({QParams.VERB: self.VERB}),
            "http://testserver/registry",
        )

    def test_calls_verb_with_params(self, mock_oai_wrap, mock_verb, mock_validate):
        client.get(self.PATH, params={QParams.VERB: self.VERB, "test": "test"})
        mock_verb.assert_called_once_with(get_test_repo(), verb=self.VERB, test="test")

    def test_calls_oai_wrap_w_verb_xml(self, mock_oai_wrap, mock_verb, mock_validate):
        client.get(self.PATH, params={QParams.VERB: self.VERB})
        mock_oai_wrap.assert_called_once_with(
            mock_verb.return_value,
            QueryParams({QParams.VERB: self.VERB}),
            "http://testserver/registry",
        )


@patch("vo_registry.main.validate_query_params", return_value=None, autospec=True)
@patch("vo_registry.main.identify", return_value=VERB_ELEM, autospec=True)
@patch("vo_registry.main.oai_wrap", return_value=OAI_ELEM, autospec=True)
class TestIdentifyVerbSelection(VerbSelectionBase):
    VERB = Verbs.IDENTIFY


@patch("vo_registry.main.validate_query_params", return_value=None, autospec=True)
@patch("vo_registry.main.listmetadataformats", return_value=VERB_ELEM, autospec=True)
@patch("vo_registry.main.oai_wrap", return_value=OAI_ELEM, autospec=True)
class TestListMetadataFormatsVerbSelection(VerbSelectionBase):
    VERB = Verbs.LIST_METADATA_FORMATS


@patch("vo_registry.main.validate_query_params", return_value=None, autospec=True)
@patch("vo_registry.main.getrecord", return_value=VERB_ELEM, autospec=True)
@patch("vo_registry.main.oai_wrap", return_value=OAI_ELEM, autospec=True)
class TestGetRecordVerbSelection(VerbSelectionBase):
    VERB = Verbs.GET_RECORD


@patch("vo_registry.main.validate_query_params", return_value=None, autospec=True)
@patch("vo_registry.main.listsets", return_value=VERB_ELEM, autospec=True)
@patch("vo_registry.main.oai_wrap", return_value=OAI_ELEM, autospec=True)
class TestListSetsVerbSelection(VerbSelectionBase):
    VERB = Verbs.LIST_SETS


@patch("vo_registry.main.validate_query_params", return_value=None, autospec=True)
@patch("vo_registry.main.listrecords", return_value=VERB_ELEM, autospec=True)
@patch("vo_registry.main.oai_wrap", return_value=OAI_ELEM, autospec=True)
class TestListRecordsVerbSelection(VerbSelectionBase):
    VERB = Verbs.LIST_RECORDS


@patch("vo_registry.main.validate_query_params", return_value=None, autospec=True)
@patch("vo_registry.main.listidentifiers", return_value=VERB_ELEM, autospec=True)
@patch("vo_registry.main.oai_wrap", return_value=OAI_ELEM, autospec=True)
class TestListIdentifiersVerbSelection(VerbSelectionBase):
    VERB = Verbs.LIST_IDENTIFIERS
