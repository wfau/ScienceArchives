import requests
from lxml import etree

from vo_registry.constants import NS, OAI_NS, XSI_NS


class TestIdentifyE2E:
    def test_includes_registry(self, oai_schema, oai_base_url):
        """
        Identify should return the main registry resource
        """
        params = {"verb": "Identify"}
        r = requests.get(oai_base_url, params=params, timeout=5000)
        assert r.status_code == 200

        # Should be valid OAH-PMH xml
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        # request should match verb and host
        assert doc[1].get("verb") == "Identify"
        assert doc[1].text == oai_base_url

        # verb child tag should be Identify
        assert doc[2].tag == f"{{{OAI_NS}}}Identify"
        identify_elem = doc[2]

        # VOResource should be a vg:Registry
        find_vor = etree.XPath("oai:description/ri:Resource", namespaces=NS)
        voresource = find_vor(identify_elem)[0]
        assert voresource.get(f"{{{XSI_NS}}}type") == "vg:Registry"

    def test_returns_badarg_error(self, oai_schema, oai_base_url):
        """
        Identify should return badArgument if there are any query parameters
        """
        params = {"verb": "Identify", "identifier": "test"}
        r = requests.get(oai_base_url, params=params, timeout=5000)
        assert r.status_code == 200

        # Should be valid OAI-PMH xml
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        # Returns a badArgument error
        assert doc[2].tag == f"{{{OAI_NS}}}error"
        assert doc[2].items() == [("code", "badArgument")]

    def test_returns_valid_origins(self, oai_base_url):
        """
        The baseURL within the identify endpoint should always match the
        external endpoint of the service.
        """
        params = {"verb": "Identify"}
        r = requests.get(oai_base_url, params=params, timeout=5000)
        doc = etree.fromstring(r.content)
        base_url = next(doc.iter(f"{{{OAI_NS}}}baseURL")).text
        assert base_url == oai_base_url
