import requests
from lxml import etree

from vo_registry.constants import NS, OAI_NS


class TestListMetadataFormatsE2E:
    def test_returns_LMF_elem(self, oai_schema, oai_base_url):
        r = requests.get(oai_base_url, params={"verb": "ListMetadataFormats"})
        assert r.status_code == 200

        # Should be valid OAI-PMH xml
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        # request should match verb and host
        assert doc[1].get("verb") == "ListMetadataFormats"
        assert doc[1].text == oai_base_url

        # verb child tag should be ListMetadataFormats
        assert doc[2].tag == f"{{{OAI_NS}}}ListMetadataFormats"
        lmf_elem = doc[2]

        # Responses to the ListMetadataFormats operation must list all names
        # for formats supported by the registry; even though they are mandatory,
        # this list must include ivo_vor and oai_dc
        find_mdp = etree.XPath("oai:metadataFormat/oai:metadataPrefix", namespaces=NS)
        mdps = {elem.text for elem in find_mdp(lmf_elem)}
        assert len(mdps) == 2
        assert mdps == {"ivo_vor", "oai_dc"}

    def test_returns_LMF_for_known_id(self, oai_base_url, oai_schema, registry_id):
        # LMF optionally supports pulling MFs for individual records
        # We support the two MFs for all records, so this is trivial
        params = {"verb": "ListMetadataFormats", "identifier": registry_id}
        r = requests.get(oai_base_url, params=params)
        doc = etree.fromstring(r.content)

        oai_schema.assertValid(doc)
        assert doc[2].tag == f"{{{OAI_NS}}}ListMetadataFormats"

    def test_returns_idDoesNotExist_for_unknown_id(self, oai_base_url, oai_schema):
        # Even though LMF always returns the same data for our registry
        # If must return an error if the requested record doesn't exist
        params = {"verb": "ListMetadataFormats", "identifier": "NotARealID"}
        r = requests.get(oai_base_url, params=params)
        doc = etree.fromstring(r.content)

        oai_schema.assertValid(doc)
        assert doc[2].tag == f"{{{OAI_NS}}}error"
        assert doc[2].items() == [("code", "idDoesNotExist")]

    def test_invalid_argument(self, oai_schema, oai_base_url):
        # LMF should return badArgument for any arg besides identifier
        params = {
            "verb": "ListMetadataFormats",
            "from": "test",
        }
        r = requests.get(oai_base_url, params=params)
        assert r.status_code == 200

        # Should be valid OAI-PMH xml
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        # Returns a badArgument error
        assert doc[2].tag == f"{{{OAI_NS}}}error"
        assert doc[2].items() == [("code", "badArgument")]
