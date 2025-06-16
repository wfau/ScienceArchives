from datetime import datetime, timedelta, timezone
import requests

from lxml import etree

from vo_registry.constants import NS, OAI_NS


class TestListIdentifiers:
    def test_e2e(self, oai_schema, oai_base_url, registry_id, authority_id):
        params = {
            "verb": "ListIdentifiers",
            "metadataPrefix": "ivo_vor",
            "set": "ivo_managed",
        }
        r = requests.get(oai_base_url, params=params, timeout=5000)
        assert r.status_code == 200

        # Should be valid OAI-PMH xml
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        # request should match verb and host
        assert doc[1].get("verb") == "ListIdentifiers"
        assert doc[1].text == oai_base_url

        # verb child tag should be ListIdentifiers
        assert doc[2].tag == f"{{{OAI_NS}}}ListIdentifiers"

        # other ListIdentifier tests
        id_elems = doc[2].xpath("oai:header/oai:identifier", namespaces=NS)
        identifiers = [i.text for i in id_elems]
        # should all be unique
        assert len(identifiers) == len(set(identifiers))
        # should have a registry and an authority
        assert registry_id in identifiers
        assert authority_id in identifiers

    def test_with_time_filters(
        self, oai_schema, oai_base_url, registry_voresource, registry_id
    ):
        # get the timestamp for the registry resource
        registry_updated_datetime = registry_voresource.get("updated")

        # from and until are inclusive, so registry should show up in both
        # requests
        params = {
            "verb": "ListIdentifiers",
            "metadataPrefix": "ivo_vor",
            "set": "ivo_managed",
            "from": registry_updated_datetime,
        }
        r = requests.get(oai_base_url, params=params, timeout=5000)
        assert r.status_code == 200

        # Should be valid OAI-PMH xml
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        # request should match verb and host
        assert doc[1].get("verb") == "ListIdentifiers"
        assert doc[1].text == oai_base_url

        # verb child tag should be ListIdentifiers
        assert doc[2].tag == f"{{{OAI_NS}}}ListIdentifiers"

        id_elems = doc[2].xpath("oai:header/oai:identifier", namespaces=NS)
        identifiers = {i.text for i in id_elems}
        assert registry_id in identifiers

        from_ids = identifiers

        params = {
            "verb": "ListIdentifiers",
            "metadataPrefix": "ivo_vor",
            "set": "ivo_managed",
            "until": registry_updated_datetime,
        }
        r = requests.get(oai_base_url, params=params, timeout=5000)
        assert r.status_code == 200

        # Should be valid OAI-PMH xml
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)
        assert doc[2].tag == f"{{{OAI_NS}}}ListIdentifiers"

        id_elems = doc[2].xpath("oai:header/oai:identifier", namespaces=NS)
        identifiers = {i.text for i in id_elems}
        assert registry_id in identifiers

        until_ids = identifiers

        assert from_ids != until_ids

    def test_missing_metadataPrefix(self, oai_schema, oai_base_url):
        params = {"verb": "ListIdentifiers"}
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
            "verb": "ListIdentifiers",
            "metadataPrefix": "really_wrong_mdp",
        }
        r = requests.get(oai_base_url, params=params, timeout=5000)
        assert r.status_code == 200

        # Should be valid OAI-PMH xml
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        errors = list(doc.xpath("oai:error", namespaces=NS))
        assert len(errors) == 1
        assert errors[0].tag == f"{{{OAI_NS}}}error"
        assert errors[0].items() == [("code", "cannotDisseminateFormat")]

    def test_unknown_set(self, oai_schema, oai_base_url):
        params = {
            "verb": "ListIdentifiers",
            "metadataPrefix": "ivo_vor",
            "set": "not_a_real_set",
        }
        r = requests.get(oai_base_url, params=params, timeout=5000)
        assert r.status_code == 200

        # Should be valid OAI-PMH xml
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        errors = list(doc.xpath("oai:error", namespaces=NS))
        assert len(errors) == 1
        assert errors[0].tag == f"{{{OAI_NS}}}error"
        assert errors[0].items() == [("code", "noSetHierarchy")]

    def test_bad_resumption_token(self, oai_schema, oai_base_url):
        params = {
            "verb": "ListIdentifiers",
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

    def test_duplicate_args(self, oai_schema, oai_base_url):
        params = [
            ("verb", "ListIdentifiers"),
            ("metadataPrefix", "ivo_vor"),
            ("metadataPrefix", "ivo_vor"),
        ]
        r = requests.get(oai_base_url, params=params, timeout=5000)
        assert r.status_code == 200

        # Should be valid OAI-PMH xml
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        errors = list(doc.xpath("oai:error", namespaces=NS))
        assert len(errors) == 1
        assert errors[0].tag == f"{{{OAI_NS}}}error"
        assert errors[0].items() == [("code", "badArgument")]

    def test_invalid_datetime(self, oai_schema, oai_base_url):
        params = [
            ("verb", "ListIdentifiers"),
            ("metadataPrefix", "ivo_vor"),
            ("from", "2024-02-12 13:49:37.305429"),
        ]
        r = requests.get(oai_base_url, params=params, timeout=5000)
        assert r.status_code == 200

        # Should be valid OAI-PMH xml
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        errors = list(doc.xpath("oai:error", namespaces=NS))
        assert len(errors) == 1
        assert errors[0].tag == f"{{{OAI_NS}}}error"
        assert errors[0].items() == [("code", "badArgument")]

    def test_until_before_from(self, oai_schema, oai_base_url):
        params = [
            ("verb", "ListIdentifiers"),
            ("metadataPrefix", "ivo_vor"),
            ("from", "2024-05-25T17:12:48Z"),
            ("until", "2024-01-25T17:12:48Z"),
        ]
        r = requests.get(oai_base_url, params=params, timeout=5000)
        assert r.status_code == 200

        # Should be valid OAI-PMH xml
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        errors = list(doc.xpath("oai:error", namespaces=NS))
        assert len(errors) > 0
        assert errors[0].tag == f"{{{OAI_NS}}}error"
        assert errors[0].items() == [("code", "badArgument")]

    def test_different_datetime_granularity(self, oai_schema, oai_base_url):
        params = [
            ("verb", "ListIdentifiers"),
            ("metadataPrefix", "ivo_vor"),
            ("from", "1975-01-25T17:12:48Z"),
            ("until", "2124-05-25"),
        ]
        r = requests.get(oai_base_url, params=params, timeout=5000)
        assert r.status_code == 200

        # Should be valid OAI-PMH xml
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        errors = list(doc.xpath("oai:error", namespaces=NS))
        assert len(errors) == 1
        assert errors[0].tag == f"{{{OAI_NS}}}error"
        assert errors[0].items() == [("code", "badArgument")]

    def test_invalid_from_and_until(self, oai_schema, oai_base_url):
        params = [
            ("verb", "ListIdentifiers"),
            ("metadataPrefix", "ivo_vor"),
            ("from", "2024-01-25T17:1"),
            ("until", "2024-05-80"),
        ]
        r = requests.get(oai_base_url, params=params, timeout=5000)
        assert r.status_code == 200

        # Should be valid OAI-PMH xml
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        errors = list(doc.xpath("oai:error", namespaces=NS))
        assert len(errors) == 2
        assert errors[0].tag == f"{{{OAI_NS}}}error"
        assert errors[0].items() == [("code", "badArgument")]

    def test_until_before_earliest(self, oai_schema, oai_base_url):
        params = [
            ("verb", "ListIdentifiers"),
            ("metadataPrefix", "ivo_vor"),
            ("until", "1983-11-12"),
        ]
        r = requests.get(oai_base_url, params=params, timeout=5000)
        assert r.status_code == 200

        # Should be valid OAI-PMH xml
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        errors = list(doc.xpath("oai:error", namespaces=NS))
        assert len(errors) == 1
        assert errors[0].tag == f"{{{OAI_NS}}}error"
        assert errors[0].items() == [("code", "noRecordsMatch")]

    def test_listidentifiers_from_after_latest(self, oai_schema, oai_base_url):
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        params = [
            ("verb", "ListIdentifiers"),
            ("metadataPrefix", "ivo_vor"),
            ("from", now),
        ]
        r = requests.get(oai_base_url, params=params, timeout=5000)
        assert r.status_code == 200

        # Should be valid OAI-PMH xml
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        errors = list(doc.xpath("oai:error", namespaces=NS))
        assert len(errors) == 1
        assert errors[0].tag == f"{{{OAI_NS}}}error"
        assert errors[0].items() == [("code", "noRecordsMatch")]

    def test_listidentifiers_no_records_small_window(self, oai_schema, oai_base_url):
        # get earliest and latest timestamps
        params = {
            "verb": "ListIdentifiers",
            "metadataPrefix": "ivo_vor",
            "set": "ivo_managed",
        }
        r = requests.get(oai_base_url, params=params, timeout=5000)
        doc = etree.fromstring(r.content)
        dt_strs = doc[2].xpath("oai:header/oai:datestamp", namespaces=NS)
        datetimes = [datetime.strptime(dt.text, "%Y-%m-%dT%H:%M:%SZ") for dt in dt_strs]
        min_datetime = min(datetimes)
        max_datetime = max(datetimes)

        # construct small (2 second) time window between them
        from_datetime = min_datetime + timedelta(seconds=20)
        until_datetime = min_datetime + timedelta(seconds=22)
        assert from_datetime < max_datetime
        assert until_datetime < max_datetime

        # test returns no records
        params = [
            ("verb", "ListIdentifiers"),
            ("metadataPrefix", "ivo_vor"),
            ("from", from_datetime.isoformat(timespec="seconds") + "Z"),
            ("until", until_datetime.isoformat(timespec="seconds") + "Z"),
        ]
        r = requests.get(oai_base_url, params=params, timeout=5000)
        assert r.status_code == 200

        # Should be valid OAI-PMH xml
        doc = etree.fromstring(r.content)
        oai_schema.assertValid(doc)

        errors = list(doc.xpath("oai:error", namespaces=NS))
        assert len(errors) == 1
        assert errors[0].tag == f"{{{OAI_NS}}}error"
        assert errors[0].items() == [("code", "noRecordsMatch")]
