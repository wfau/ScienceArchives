from lxml import etree

from vo_registry.constants import OAI_NS, Verbs
from vo_registry.verbs.listsets import listsets


class TestListSets:
    def test_returns_element(self, test_repo):
        result = listsets(test_repo)[0]
        assert isinstance(result, etree._Element)
        assert result.tag == f"{{{OAI_NS}}}{Verbs.LIST_SETS}"

    def test_includes_ivo_managed_set(self, test_repo):
        result = listsets(test_repo)[0]
        result_set = result[0]
        assert result_set[0].tag == f"{{{OAI_NS}}}setSpec"
        assert result_set[0].text == "ivo_managed"
        assert result_set[1].tag == f"{{{OAI_NS}}}setName"
        assert result_set[1].text == "ivo_managed"
