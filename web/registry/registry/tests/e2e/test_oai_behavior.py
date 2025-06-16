import requests
from datetime import datetime, timezone, timedelta
from lxml import etree

from vo_registry.constants import OAI_NS


def test_registry_returns_same_result_for_get_and_post(oai_schema, oai_base_url):
    # Repositories must support both the GET and POST methods.
    r = requests.get(oai_base_url, params={"verb": "Identify"})
    assert r.status_code == 200
    r_post = requests.get(oai_base_url, params={"verb": "Identify"})
    assert r_post.status_code == 200

    doc = etree.fromstring(r.content)
    doc_post = etree.fromstring(r_post.content)

    # Should be valid OAI-PMH
    oai_schema.assertValid(doc)
    oai_schema.assertValid(doc_post)

    doc[0].text = "blank"
    doc_post[0].text = "blank"
    assert etree.tostring(doc) == etree.tostring(doc_post)


def test_responseDate_is_recent(oai_base_url):
    r = requests.get(oai_base_url, params={"verb": "Identify"})
    assert r.status_code == 200

    doc = etree.fromstring(r.content)
    response_datetime = datetime.fromisoformat(doc[0].text)

    now = datetime.now(timezone.utc)
    time_diff = now - response_datetime
    assert time_diff < timedelta(seconds=2)


def test_invalid_verb_returns_badVerb_error(oai_schema, oai_base_url):
    # Registry should return badVerb if the verb is unknown
    r = requests.get(oai_base_url, params={"verb": "NotARealVerb"})
    assert r.status_code == 200

    # Should be valid xml
    doc = etree.fromstring(r.content)

    # Should be valid OAI-PMH
    oai_schema.assertValid(doc)

    # Returns a badVerb error
    assert doc[1].attrib == []
    assert doc[2].tag == f"{{{OAI_NS}}}error"
    assert doc[2].items() == [("code", "badVerb")]
