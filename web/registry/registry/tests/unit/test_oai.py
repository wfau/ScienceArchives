from datetime import datetime, timezone, timedelta

from vo_registry.constants import OAI_NS, XSI_NS
from vo_registry.oai import oai_wrap
from vo_registry.utils import read_xml_from_file


TEST_ELEMENT = [read_xml_from_file("identify.xml", module="tests")]


class TestOaiWrap:
    def test_first_tag(self):
        # https://www.openarchives.org/OAI/openarchivesprotocol.html#XMLResponse
        # The first tag output is an XML declaration where the version is
        # always 1.0 and the encoding is always UTF-8,
        # eg: <?xml version="1.0" encoding="UTF-8" ?>
        result = oai_wrap(TEST_ELEMENT, {}, "localhost")
        assert result.docinfo.encoding == "UTF-8"
        assert result.docinfo.xml_version == "1.0"

    def test_root_element(self):
        # The remaining content is enclosed in a root element with the
        # name OAI-PMH. This element must have three attributes that define
        # the XML namespaces used in the remainder of the response and the
        # location of the validating schema:
        # xmlns, xmlns:xsi, xsi:schemaLocation
        result = oai_wrap(TEST_ELEMENT, {}, "localhost")
        root = result.getroot()
        assert root.nsmap == {None: OAI_NS, "xsi": XSI_NS}
        assert root.items() == [
            (
                f"{{{XSI_NS}}}schemaLocation",
                f"{OAI_NS} https://www.openarchives.org/OAI/2.0/OAI-PMH.xsd",
            )
        ]
        assert root.tag == f"{{{OAI_NS}}}OAI-PMH"

    def test_first_date_child(self):
        # responseDate -- a UTCdatetime indicating the time and date that
        # the response was sent. This must be expressed in UTC.
        result = oai_wrap(TEST_ELEMENT, {}, "localhost")
        child = result.getroot()[0]
        assert child.tag == f"{{{OAI_NS}}}responseDate"
        result_datetime = datetime.fromisoformat(child.text)
        diff = datetime.now(timezone.utc) - result_datetime
        assert diff < timedelta(seconds=1)

    def test_second_request_child_valid(self):
        # request -- indicating the protocol request that generated this
        # response. The rules for generating the request element are as follows:
        # The content of the request element must always be the base URL
        # of the protocol request;
        # The only valid attributes for the request element are the keys
        # of the key=value pairs of protocol request. The attribute values
        # must be the corresponding values of those key=value pairs;
        # In cases where the request that generated this response did not
        # result in an error or exception condition, the attributes and
        # attribute values of the request element must match the key=value
        # pairs of the protocol request;
        result = oai_wrap(TEST_ELEMENT, {"metadataPrefix": "something"}, "localhost")
        child = result.getroot()[1]
        assert child.tag == f"{{{OAI_NS}}}request"
        assert child.text == "localhost"
        assert dict(child.items()) == {"metadataPrefix": "something"}

    def test_second_request_child_for_error_elements(self):
        # In cases where the request that generated this response resulted
        # in a badVerb or badArgument error condition, the repository must
        # return the base URL of the protocol request only.
        # Attributes must not be provided in these cases.
        error_element = [
            read_xml_from_file("badVerb.xml", module="tests"),
            read_xml_from_file("badArgument.xml", module="tests"),
        ]
        result = oai_wrap(error_element, {"metadataPrefix": "something"}, "localhost")
        child = result.getroot()[1]
        assert child.tag == f"{{{OAI_NS}}}request"
        assert child.text == "localhost"
        assert dict(child.items()) == {}

    def test_third_child_is_inserted(self):
        result = oai_wrap(TEST_ELEMENT, {}, "localhost")
        child = result.getroot()[2]
        assert child == TEST_ELEMENT[0]

    def test_is_valid_OAI_PMH(self, oai_schema):
        result = oai_wrap(TEST_ELEMENT, {}, "localhost")
        oai_schema.assertValid(result)

    def test_multiple_errors_are_valid_OAI_PMH(self, oai_schema):
        error_element = [
            read_xml_from_file("badVerb.xml", module="tests"),
            read_xml_from_file("badArgument.xml", module="tests"),
        ]
        result = oai_wrap(error_element, {"metadataPrefix": "something"}, "localhost")
        oai_schema.assertValid(result)
