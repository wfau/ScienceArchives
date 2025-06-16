import os
from lxml import etree

from vo_registry.constants import OAI_NS, RI_NS, Verbs
from vo_registry.verbs.identify import identify


class TestIdentify:
    def test_returns_an_identify_element(self, test_repo):
        result = identify(test_repo)[0]
        assert isinstance(result, etree._Element)
        assert result.tag == f"{{{OAI_NS}}}{Verbs.IDENTIFY}"

    def test_includes_registry_resource_in_description(self, test_repo):
        result = identify(test_repo)[0]
        description = next(result.iter(f"{{{OAI_NS}}}description"))
        assert description[0].tag == f"{{{RI_NS}}}Resource"

    def test_included_resource_is_loaded_from_test(self, test_repo):
        result = identify(test_repo)[0]
        resource = next(result.iter(f"{{{RI_NS}}}Resource"))
        assert resource[0].text == "Test Registry"

    def test_provides_accurate_origins(self, test_repo):
        """
        The identify method should return origins that match runtime settings
        """
        result = identify(test_repo)[0]
        base_url = next(result.iter(f"{{{OAI_NS}}}baseURL")).text
        # Ensure the baseURL in the context of identify points to the base of
        # the registry. BASE_URL in this case is the base of the API service
        assert f"{os.environ.get('BASE_URL')}/registry" in base_url
