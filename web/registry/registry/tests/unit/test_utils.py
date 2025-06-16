from datetime import datetime

import pytest
from lxml import etree

from vo_registry.constants import OAI_NS, RI_NS
from vo_registry.utils import findtext_or_raise, parse_datetime, read_xml_from_file


class TestReadXMLFromFile:
    def test_returns_element_from_vo_registry_module(self):
        result = read_xml_from_file("identify.xml")
        assert isinstance(result, etree._Element)
        assert result.tag == f"{{{OAI_NS}}}Identify"

    def test_returns_element_from_tests_module(self):
        result = read_xml_from_file("resources/authority.xml", module="tests")
        assert isinstance(result, etree._Element)
        assert result.tag == f"{{{RI_NS}}}Resource"
        assert result[0].text == "TestOrg"

    def test_reads_json_file(self):
        result = read_xml_from_file("resources/registry.json", module="tests")
        assert isinstance(result, etree._Element)
        assert result.tag == f"{{{RI_NS}}}Resource"
        assert result[0].text == "Test Registry"

    def test_reads_yaml_file(self):
        result = read_xml_from_file("resources/deleted.yaml", module="tests")
        assert isinstance(result, etree._Element)
        assert result.tag == f"{{{RI_NS}}}Resource"
        assert result[0].text == "Deleted Archive"


class TestParsingDatetime:
    def test_datetime(self):
        result = parse_datetime("2024-03-25T17:12:48Z")
        assert isinstance(result, datetime)

    def test_date(self):
        result = parse_datetime("2024-03-25")
        assert isinstance(result, datetime)

    def test_invalid_string(self):
        with pytest.raises(ValueError):
            parse_datetime("2024-02-12 13:49:37.305429")


class TestFindTextOrRaise:
    def test_finds_text(self):
        root = etree.Element("Pirate")
        child = etree.SubElement(root, "Ship")
        child.text = "ahoy"
        result = findtext_or_raise(root, "Ship")
        assert result == "ahoy"

    def test_raises(self):
        root = etree.Element("Pirate")
        etree.SubElement(root, "Ship")
        with pytest.raises(ValueError):
            findtext_or_raise(root, "Ship")
