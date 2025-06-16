import requests
from lxml import etree

from vo_registry.constants import NS, OAI_DC_NS, OAI_NS, RI_NS, XSI_NS


class TestListRecords:
    def test_e2e(self, oai_schema, oai_base_url, registry_id, authority_id):
        params = {"verb": "ListRecords", "metadataPrefix": "ivo_vor"}
        r = requests.get(oai_base_url, params=params, timeout=5000)
        assert r.status_code == 200

        # Should be valid xml
        doc = etree.fromstring(r.content)

        # Should be valid OAI-PMH
        oai_schema.assertValid(doc)

        # request should match verb and host
        assert doc[1].get("verb") == "ListRecords"
        assert doc[1].text == oai_base_url

        # verb child tag should be ListRecords
        assert doc[2].tag == f"{{{OAI_NS}}}ListRecords"

        # must include the registry record
        records = list(doc[2])
        registry_record = [r for r in records if r[0][0].text == registry_id][0]
        registry_resource = registry_record[1][0]
        assert registry_resource.tag == f"{{{RI_NS}}}Resource"
        assert registry_resource.get(f"{{{XSI_NS}}}type") == "vg:Registry"

        # and the authority record
        authority_record = [r for r in records if r[0][0].text == authority_id][0]
        authority_resource = authority_record[1][0]
        assert authority_resource.tag == f"{{{RI_NS}}}Resource"
        assert authority_resource.get(f"{{{XSI_NS}}}type") == "vg:Authority"

    def test_oai_dc(self, oai_schema, oai_base_url, registry_id, authority_id):
        params = {"verb": "ListRecords", "metadataPrefix": "oai_dc"}
        r = requests.get(oai_base_url, params=params, timeout=5000)
        assert r.status_code == 200

        # Should be valid xml
        doc = etree.fromstring(r.content)

        # Should be valid OAI-PMH
        oai_schema.assertValid(doc)

        # request should match verb and host
        assert doc[1].get("verb") == "ListRecords"
        assert doc[1].text == oai_base_url

        # verb child tag should be ListRecords
        assert doc[2].tag == f"{{{OAI_NS}}}ListRecords"

        # must include the registry record
        records = list(doc[2])
        registry_record = [r for r in records if r[0][0].text == registry_id][0]
        registry_resource = registry_record[1][0]
        assert registry_resource.tag == f"{{{OAI_DC_NS}}}dc"

    def test_missing_metadataPrefix(self, oai_schema, oai_base_url):
        params = {"verb": "ListRecords"}
        r = requests.get(oai_base_url, params=params, timeout=5000)
        assert r.status_code == 200

        # Should be valid OAI-PMH xml
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        errors = list(doc.xpath("oai:error", namespaces=NS))
        assert len(errors) == 1
        assert errors[0].tag == f"{{{OAI_NS}}}error"
        assert errors[0].items() == [("code", "badArgument")]

    def test_unknown_metadataPrefix(self, oai_schema, oai_base_url):
        params = {
            "verb": "ListRecords",
            "metadataPrefix": "really_wrong_mdp",
        }
        r = requests.get(oai_base_url, params=params, timeout=5000)
        assert r.status_code == 200

        # Should be valid OAI-PMH
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        errors = list(doc.xpath("oai:error", namespaces=NS))
        assert len(errors) == 1
        assert errors[0].tag == f"{{{OAI_NS}}}error"
        assert errors[0].items() == [("code", "cannotDisseminateFormat")]

    def test_unknown_set(self, oai_schema, oai_base_url):
        params = {
            "verb": "ListRecords",
            "metadataPrefix": "ivo_vor",
            "set": "not_a_real_set",
        }
        r = requests.get(oai_base_url, params=params, timeout=5000)
        assert r.status_code == 200

        # Should be valid OAI-PMH
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        errors = list(doc.xpath("oai:error", namespaces=NS))
        assert len(errors) == 1
        assert errors[0].tag == f"{{{OAI_NS}}}error"
        assert errors[0].items() == [("code", "noSetHierarchy")]

    def test_bad_resumption_token(self, oai_schema, oai_base_url):
        params = {
            "verb": "ListRecords",
            "resumptionToken": "not_a_real_token",
        }
        r = requests.get(oai_base_url, params=params, timeout=5000)
        assert r.status_code == 200

        # Should be valid OAI-PMH
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        errors = list(doc.xpath("oai:error", namespaces=NS))
        assert len(errors) == 2
        assert errors[1].tag == f"{{{OAI_NS}}}error"
        assert errors[1].items() == [("code", "badResumptionToken")]
