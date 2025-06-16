import requests
from lxml import etree

from vo_registry.constants import OAI_NS


def test_listsets_e2e(oai_schema, oai_base_url):
    r = requests.get(oai_base_url, params={"verb": "ListSets"})
    assert r.status_code == 200

    # Should be valid OAI-PMH xml
    doc = etree.fromstring(r.content)
    oai_schema.assertValid(doc)

    # request should match verb and host
    assert doc[1].get("verb") == "ListSets"
    assert doc[1].text == oai_base_url

    # verb child tag should be ListSets
    assert doc[2].tag == f"{{{OAI_NS}}}ListSets"
    listset_elem = doc[2]

    # other ListSets tests
    # While support for sets is optional in the OAI-PMH standard,
    # a VO registry MUST support the set with the reserved name ivo_managed
    # to be compliant with this specification.
    assert listset_elem[0].tag == f"{{{OAI_NS}}}set"
    assert listset_elem[0][0].tag == f"{{{OAI_NS}}}setSpec"
    assert listset_elem[0][0].text == "ivo_managed"
    assert listset_elem[0][1].tag == f"{{{OAI_NS}}}setName"
    assert listset_elem[0][1].text == "ivo_managed"


def test_listset_invalid_argument(oai_schema, oai_base_url):
    r = requests.get(oai_base_url, params={"verb": "ListSets", "test": "test"})
    assert r.status_code == 200

    # Should be valid OAI-PMH xml
    doc = etree.fromstring(r.content)
    oai_schema.assertValid(doc)

    # Returns a badArgument error
    assert doc[2].tag == f"{{{OAI_NS}}}error"
    assert doc[2].items() == [("code", "badArgument")]


def test_listsets_badResumptionToken_error(oai_schema, oai_base_url):
    params = {"verb": "ListSets", "resumptionToken": "nope"}
    r = requests.get(oai_base_url, params=params)
    assert r.status_code == 200

    # Should be valid OAI-PMH xml
    doc = etree.fromstring(r.content)
    oai_schema.assertValid(doc)

    # Returns a badArgument error
    assert doc[2].tag == f"{{{OAI_NS}}}error"
    assert doc[2].items() == [("code", "badResumptionToken")]


# We don't test for noSetHierarchy because we do support sets
