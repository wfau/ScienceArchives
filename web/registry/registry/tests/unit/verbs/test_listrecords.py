from lxml import etree

from vo_registry.constants import OAI_DC_NS, OAI_NS, RI_NS, MetadataFormats, Verbs
from vo_registry.verbs.listrecords import listrecords


class TestListRecords:
    def test_returns_element(self, test_repo):
        result = listrecords(test_repo)[0]
        assert isinstance(result, etree._Element)
        assert result.tag == f"{{{OAI_NS}}}{Verbs.LIST_RECORDS}"
        record = [r for r in list(result) if r[0].get("status") != "deleted"][0]
        assert record[1][0].tag == f"{{{RI_NS}}}Resource"

    def test_returns_oai_dc_element(self, test_repo):
        result = listrecords(test_repo, metadataPrefix=MetadataFormats.OAI_DC)[0]
        assert isinstance(result, etree._Element)
        assert result.tag == f"{{{OAI_NS}}}{Verbs.LIST_RECORDS}"
        record = [r for r in list(result) if r[0].get("status") != "deleted"][0]
        assert record[1][0].tag == f"{{{OAI_DC_NS}}}dc"

    def test_returns_multiple_records(self, test_repo):
        result = listrecords(test_repo)[0]
        records = list(result)
        assert len(records) > 1
        assert records[0].tag == f"{{{OAI_NS}}}record"

    def test_filter_with_from(self, test_repo):
        params = {"from": "2024-02-01"}
        result = listrecords(test_repo, **params)[0]
        assert len(result) == 2

    def test_filter_with_until(self, test_repo):
        params = {"until": "2024-02-01"}
        result = listrecords(test_repo, **params)[0]
        assert len(result) == 1
