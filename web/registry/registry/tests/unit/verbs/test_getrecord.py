from lxml import etree

from vo_registry.constants import OAI_DC_NS, OAI_NS, XSI_NS, MetadataFormats, Verbs
from vo_registry.verbs.getrecord import getrecord


class TestGetRecord:
    def test_returns_registry_record(self, test_repo):
        registry_id = test_repo.registry_id
        kwargs = {"identifier": registry_id, "metadataPrefix": MetadataFormats.IVO_VOR}
        result = getrecord(test_repo, **kwargs)[0]
        assert isinstance(result, etree._Element)
        assert result.tag == f"{{{OAI_NS}}}{Verbs.GET_RECORD}"
        records = list(result)
        assert len(records) == 1
        registry_record = records[0]
        registry_resource = registry_record[1][0]
        assert registry_resource.get(f"{{{XSI_NS}}}type") == "vg:Registry"

    def test_returns_oai_dc_format(self, test_repo):
        registry_id = test_repo.registry_id
        kwargs = {"identifier": registry_id, "metadataPrefix": MetadataFormats.OAI_DC}
        result = getrecord(test_repo, **kwargs)[0]
        records = list(result)
        assert len(records) == 1
        registry_record = records[0]
        registry_resource = registry_record[1][0]
        assert registry_resource.tag == f"{{{OAI_DC_NS}}}dc"

    def test_returns_authority_record(self, test_repo):
        authority_id = "/".join(test_repo.registry_id.split("/")[0:-1])
        kwargs = {"identifier": authority_id, "metadataPrefix": MetadataFormats.IVO_VOR}
        result = getrecord(test_repo, **kwargs)[0]
        assert isinstance(result, etree._Element)
        assert result.tag == f"{{{OAI_NS}}}{Verbs.GET_RECORD}"
        records = list(result)
        assert len(records) == 1
        registry_record = records[0]
        registry_resource = registry_record[1][0]
        assert registry_resource.get(f"{{{XSI_NS}}}type") == "vg:Authority"

    def test_deleted_record(self, test_repo):
        deleted_id = "ivo://example.edu/deleted-archive"
        kwargs = {"identifier": deleted_id, "metadataPrefix": MetadataFormats.IVO_VOR}
        result = getrecord(test_repo, **kwargs)[0]
        records = list(result)
        assert len(records) == 1
        deleted_record = records[0]
        assert len(deleted_record) == 1
        header = deleted_record[0]
        assert header.get("status") == "deleted"
