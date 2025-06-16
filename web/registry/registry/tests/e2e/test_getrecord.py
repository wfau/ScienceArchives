import requests
from lxml import etree

from vo_registry.constants import OAI_DC_NS, OAI_NS, RI_NS, XSI_NS, NS


class TestGetRecord:
    def test_getrecord_registry(self, oai_schema, oai_base_url, registry_id):
        params = {
            "verb": "GetRecord",
            "identifier": registry_id,
            "metadataPrefix": "ivo_vor",
        }
        r = requests.get(oai_base_url, params=params)
        assert r.status_code == 200

        # Should be valid OAI-PMH xml
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        # request should match verb and host
        assert doc[1].get("verb") == "GetRecord"
        assert doc[1].text == oai_base_url

        # verb child tag should be GetRecord
        assert doc[2].tag == f"{{{OAI_NS}}}GetRecord"

        # must return the registry record
        records = list(doc[2])
        assert len(records) == 1
        registry_record = records[0]
        registry_resource = registry_record[1][0]
        assert registry_resource.tag == f"{{{RI_NS}}}Resource"
        assert registry_resource.get(f"{{{XSI_NS}}}type") == "vg:Registry"

        # now, get the Authority Record

    def test_getrecord_authority(self, oai_schema, oai_base_url, authority_id):
        params = {
            "verb": "GetRecord",
            "identifier": authority_id,
            "metadataPrefix": "ivo_vor",
        }
        r = requests.get(oai_base_url, params=params)
        assert r.status_code == 200

        # Should be valid OAI-PMH xml
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        # must return the authority record
        records = list(doc[2])
        assert len(records) == 1
        registry_record = records[0]
        registry_resource = registry_record[1][0]
        assert registry_resource.tag == f"{{{RI_NS}}}Resource"
        assert registry_resource.get(f"{{{XSI_NS}}}type") == "vg:Authority"

    def test_missing_mdp(self, oai_schema, oai_base_url, registry_id):
        params = {"verb": "GetRecord", "identifier": registry_id}
        r = requests.get(oai_base_url, params=params)
        assert r.status_code == 200

        # Should be valid OAI-PMH xml
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        errors = list(doc.xpath("oai:error", namespaces=NS))
        assert len(errors) == 1
        assert errors[0].tag == f"{{{OAI_NS}}}error"
        assert errors[0].items() == [("code", "badArgument")]

    def test_unknown_mdp(self, oai_schema, oai_base_url, registry_id):
        params = {
            "verb": "GetRecord",
            "identifier": registry_id,
            "metadataPrefix": "really_wrong_mdp",
        }
        r = requests.get(oai_base_url, params=params)
        assert r.status_code == 200

        # Should be valid OAI-PMH xml
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        errors = list(doc.xpath("oai:error", namespaces=NS))
        assert len(errors) == 1
        assert errors[0].tag == f"{{{OAI_NS}}}error"
        assert errors[0].items() == [("code", "cannotDisseminateFormat")]

    def test_unknown_arg(self, oai_schema, oai_base_url, registry_id):
        params = {
            "verb": "GetRecord",
            "identifier": registry_id,
            "metadataPrefix": "ivo_vor",
            "unknown": "not_an_arg",
        }
        r = requests.get(oai_base_url, params=params)
        assert r.status_code == 200

        # Should be valid OAI-PMH xml
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        errors = list(doc.xpath("oai:error", namespaces=NS))
        assert len(errors) == 1
        assert errors[0].tag == f"{{{OAI_NS}}}error"
        assert errors[0].items() == [("code", "badArgument")]

    def test_getrecord_oai_dc(self, oai_schema, oai_base_url, registry_id):
        params = {
            "verb": "GetRecord",
            "identifier": registry_id,
            "metadataPrefix": "oai_dc",
        }
        r = requests.get(oai_base_url, params=params)
        assert r.status_code == 200

        # Should be valid OAI-PMH xml
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        # request should match verb and host
        assert doc[1].get("verb") == "GetRecord"
        assert doc[1].text == oai_base_url

        # verb child tag should be GetRecord
        assert doc[2].tag == f"{{{OAI_NS}}}GetRecord"

        # must return the registry record
        records = list(doc[2])
        assert len(records) == 1
        registry_record = records[0]
        registry_resource = registry_record[1][0]
        assert registry_resource.tag == f"{{{OAI_DC_NS}}}dc"
