from lxml import etree

from vo_registry.constants import NS, OAI_NS, Verbs
from vo_registry.verbs.listidentifiers import listidentifiers


class TestListIdentifiers:
    def test_returns_correct_element(self, test_repo):
        result = listidentifiers(test_repo)[0]
        assert isinstance(result, etree._Element)
        assert result.tag == f"{{{OAI_NS}}}{Verbs.LIST_IDENTIFIERS}"

    def test_registry_id_in_identifiers(self, test_repo):
        result = listidentifiers(test_repo)[0]
        id_elems = result.xpath("oai:header/oai:identifier", namespaces=NS)
        assert test_repo.registry_id in [i.text for i in id_elems]

    def test_filter_with_from(self, test_repo):
        params = {"from": "2024-02-01"}
        result = listidentifiers(test_repo, **params)[0]
        id_elems = result.xpath("oai:header/oai:identifier", namespaces=NS)
        assert len(id_elems) == 2

    def test_filter_with_until(self, test_repo):
        params = {"until": "2024-02-01"}
        result = listidentifiers(test_repo, **params)[0]
        id_elems = result.xpath("oai:header/oai:identifier", namespaces=NS)
        assert len(id_elems) == 1
