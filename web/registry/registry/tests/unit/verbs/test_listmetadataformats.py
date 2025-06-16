from lxml import etree

from vo_registry.constants import OAI_NS, MetadataFormats, Verbs
from vo_registry.verbs.listmetadataformats import listmetadataformats


class TestListMetadataFormats:
    def test_returns_element(self, test_repo):
        result = listmetadataformats(test_repo)[0]
        assert isinstance(result, etree._Element)
        assert result.tag == f"{{{OAI_NS}}}{Verbs.LIST_METADATA_FORMATS}"

    def test_returns_both_metadataformats(self, test_repo):
        result = listmetadataformats(test_repo)[0]
        formats = {ee[0].text for ee in result}
        assert formats == set(MetadataFormats)
        assert len(formats) == 2

    def test_returns_both_metadataformats_for_known_id(self, test_repo):
        reg_id = test_repo.registry_id
        result = listmetadataformats(test_repo, identifier=reg_id)[0]
        formats = {ee[0].text for ee in result}
        assert formats == set(MetadataFormats)
