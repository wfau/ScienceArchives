from datetime import datetime
from tempfile import NamedTemporaryFile
from importlib import resources

import pytest
from lxml import etree

from vo_registry.constants import DC_NS, OAI_DC_NS, OAI_NS, RI_NS, NS
from vo_registry.errors import IdentifierNotFound
from vo_registry.resources import VOResource, ResourceRepo
from vo_registry.utils import read_xml_from_file


TEST_REGISTRY_ID = "ivo://example.edu/registry"


class TestResourceRepo:
    def test_get_all_returns_same_number_records_in_files(self):
        trav = resources.files("tests") / "static/resources"
        repo = ResourceRepo("tests")
        assert len(repo.get_all()) == len(list(trav.iterdir())), "check for temp files"

    def test_get_registry_record_by_id(self, voresource_schema):
        repo = ResourceRepo("tests")
        registry_record = repo.get(TEST_REGISTRY_ID)
        registry_resource = registry_record[1][0]
        voresource_schema.assertValid(registry_resource)
        assert registry_resource[0].text == "Test Registry"

    def test_get_record_in_oai_dc_format(self, oai_dc_schema):
        repo = ResourceRepo("tests")
        registry_record = repo.get(TEST_REGISTRY_ID, mdp="oai_dc")
        registry_resource = registry_record[1][0]
        oai_dc_schema.assertValid(registry_resource)
        assert registry_resource[0].text == "Test Registry"
        assert registry_resource.tag == f"{{{OAI_DC_NS}}}dc"

    def test_get_all_returns_record_elements(self):
        repo = ResourceRepo("tests")
        records = repo.get_all()
        record = [r for r in records if r[0].get("status") != "deleted"][0]
        assert record.tag == f"{{{OAI_NS}}}record"
        assert record[1][0].tag == f"{{{RI_NS}}}Resource"

    def test_get_all_in_oai_dc_format(self):
        repo = ResourceRepo("tests")
        records = repo.get_all(mdp="oai_dc")
        record = [r for r in records if r[0].get("status") != "deleted"][0]
        assert record[1][0].tag == f"{{{OAI_DC_NS}}}dc"

    def test_get_all_filters_after_from(self, test_repo):
        num_all_results = len(test_repo.get_all())
        result = test_repo.get_all(from_str="2024-01-20")
        assert result[0].tag == f"{{{OAI_NS}}}record"
        assert len(result) < num_all_results

    def test_get_all_filters_before_until(self, test_repo):
        num_all_results = len(test_repo.get_all())
        result = test_repo.get_all(until_str="2024-01-20")
        assert result[0].tag == f"{{{OAI_NS}}}record"
        assert len(result) < num_all_results

    def test_get_all_filters_between_from_and_until(self, test_repo):
        num_all_results = len(test_repo.get_all())
        result = test_repo.get_all(from_str="2024-01-20", until_str="2024-04-02")
        assert result[0].tag == f"{{{OAI_NS}}}record"
        assert len(result) < num_all_results

    def test_get_raises_if_id_unknown(self, test_repo):
        with pytest.raises(IdentifierNotFound):
            test_repo.get("not_a_real_id")

    def test_earliest_datetime(self, test_repo):
        assert isinstance(test_repo.earliest_datetime, datetime)
        assert test_repo.earliest_datetime == datetime(2024, 1, 1)

    def test_latest_datetime(self, test_repo):
        assert isinstance(test_repo.earliest_datetime, datetime)
        assert test_repo.latest_datetime == datetime(2024, 2, 17)

    def test_registry_id(self, test_repo):
        assert test_repo.registry_id == "ivo://example.edu/registry"

    def test_duplicate_identifiers_raises_error(self):
        root = read_xml_from_file("/resources/authority.xml", module="tests")

        with NamedTemporaryFile(dir="tests/static/resources/", suffix=".xml") as tf:
            with pytest.raises(KeyError):
                tf.write(etree.tostring(root))
                tf.flush()
                ResourceRepo("tests")


class TestVOResourceClass:
    def test_init_from_resource_root(self):
        root = read_xml_from_file("resources/registry.json", module="tests")
        resource = VOResource(root)
        assert resource.updated == datetime(2024, 1, 1)
        assert resource.identifier == "ivo://example.edu/registry"
        assert resource.resource_type == "vg:Registry"

    def test_to_record(self):
        root = read_xml_from_file("resources/registry.json", module="tests")
        resource = VOResource(root)
        record = resource.to_record()
        assert len(record) == 2
        assert record[0].tag == f"{{{OAI_NS}}}header"
        assert record[1].tag == f"{{{OAI_NS}}}metadata"
        assert record[1][0].tag == f"{{{RI_NS}}}Resource"

    def test_deleted_to_record(self):
        root = read_xml_from_file("resources/deleted.yaml", module="tests")
        resource = VOResource(root)
        record = resource.to_record()
        assert len(record) == 1
        assert record[0].tag == f"{{{OAI_NS}}}header"
        assert record[0].get("status") == "deleted"

    def test_header(self):
        root = read_xml_from_file("resources/registry.json", module="tests")
        resource = VOResource(root)
        header = resource.header
        assert header.tag == f"{{{OAI_NS}}}header"
        assert header.attrib == []

    def test_deleted_header(self):
        root = read_xml_from_file("resources/deleted.yaml", module="tests")
        resource = VOResource(root)
        header = resource.header
        assert header.get("status") == "deleted"

    def test_to_oai_dc_record_minimum(self, voresource_schema, oai_dc_schema):
        # without optional fields
        root = read_xml_from_file("oai_dc_test_min.xml", module="tests")
        voresource_schema.assertValid(root)
        resource = VOResource(root)
        record = resource.to_record(mdp="oai_dc")
        oai_dc_root = record[1][0]
        oai_dc_schema.assertValid(oai_dc_root)
        assert oai_dc_root.tag == f"{{{OAI_DC_NS}}}dc"
        # Title
        assert oai_dc_root.findtext(f"{{{DC_NS}}}title") == "Test Registry Title"
        # Creator(s)
        creators = oai_dc_root.xpath("dc:creator", namespaces=NS)
        assert len(creators) == 0
        # Subject
        assert oai_dc_root.findtext(f"{{{DC_NS}}}subject") == "registrysubject"
        # Description
        description = "Test Registry Description"
        assert oai_dc_root.findtext(f"{{{DC_NS}}}description") == description
        # Publisher
        assert oai_dc_root.findtext(f"{{{DC_NS}}}publisher") == "TestOrg"
        # Contributor
        contributors = oai_dc_root.xpath("dc:contributor", namespaces=NS)
        assert len(contributors) == 0
        # Date
        assert oai_dc_root.findtext(f"{{{DC_NS}}}date") == "2024-01-01T00:00:00Z"
        # Type
        assert oai_dc_root.findtext(f"{{{DC_NS}}}type") == "vg:Registry"
        # Identifier
        identifier = "ivo://example.edu/registry"
        assert oai_dc_root.findtext(f"{{{DC_NS}}}identifier") == identifier

    def test_to_oai_dc_record_multi(self, voresource_schema, oai_dc_schema):
        # with multiples in fields that support that
        root = read_xml_from_file("oai_dc_test_max.xml", module="tests")
        voresource_schema.assertValid(root)
        resource = VOResource(root)
        record = resource.to_record(mdp="oai_dc")
        oai_dc_root = record[1][0]
        oai_dc_schema.assertValid(oai_dc_root)
        assert oai_dc_root.tag == f"{{{OAI_DC_NS}}}dc"
        # Creator(s)
        creators = oai_dc_root.xpath("dc:creator", namespaces=NS)
        assert len(creators) == 2
        creators_text = set([c.text for c in creators])
        assert creators_text == set(["Creator, Test", "Creator2, Test"])
        # Subject(s)
        subjects = oai_dc_root.xpath("dc:subject", namespaces=NS)
        assert len(subjects) == 2
        subject_text = set([s.text for s in subjects])
        assert subject_text == set(["registry", "registry2"])
        # Contributor(s)
        contributors = oai_dc_root.xpath("dc:contributor", namespaces=NS)
        assert len(contributors) == 2
        contributor_text = set([c.text for c in contributors])
        assert contributor_text == set(["contributor", "contributor2"])
