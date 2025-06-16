from importlib import resources

import pytest
from lxml import etree

from vo_registry.resources import ResourceRepo
from vo_registry.utils import read_xml_from_file


@pytest.fixture(scope="session")
def test_repo():
    return ResourceRepo("tests")


class LocalResolver(etree.Resolver):
    def __init__(self):
        ivoa = "http://www.ivoa.net/xml/"
        dc = "http://dublincore.org/schemas/xmls"
        self.schema_lookup = {
            f"{ivoa}RegistryInterface/v1.0": "schemas/RegistryInterface.xsd",
            f"{ivoa}VORegistry/v1.0": "schemas/VORegistry.xsd",
            f"{ivoa}VOResource/v1.0": "schemas/VOResource-v1.1.xsd",
            f"{ivoa}VODataService/v1.1": "schemas/VODataService-v1.2.xsd",
            f"{ivoa}SIA/v1.1": "schemas/SIA-v1.1.xsd",
            f"{ivoa}ConeSearch/v1.0": "schemas/ConeSearch-v1.0.xsd",
            f"{ivoa}STC/stc-v1.30.xsd": "schemas/stc-v1.30.xsd",
            f"{ivoa}Xlink/xlink.xsd": "schemas/xlink.xsd",
            f"{dc}/simpledc20021212.xsd": "schemas/simpledc20021212.xsd",
            "http://www.w3.org/2001/03/xml.xsd": "schemas/xml.xsd",
        }

    def resolve(self, url, id, context):
        local_file = self.schema_lookup[url]
        schema_xml = read_xml_from_file(local_file)
        schema_string = etree.tostring(schema_xml)
        return self.resolve_string(schema_string, context)


@pytest.fixture(scope="session")
def oai_schema():
    parser = etree.XMLParser()
    parser.resolvers.add(LocalResolver())

    OAI_trav = resources.files("vo_registry") / "static/schemas/OAI-PMH.xsd"
    with resources.as_file(OAI_trav) as f:
        oai_xsd = etree.parse(f.open("rb"), parser=parser)

    registryinterface_import = etree.Element(
        "{http://www.w3.org/2001/XMLSchema}import",
        namespace="http://www.ivoa.net/xml/RegistryInterface/v1.0",
        schemaLocation="http://www.ivoa.net/xml/RegistryInterface/v1.0",
    )
    voregistry_import = etree.Element(
        "{http://www.w3.org/2001/XMLSchema}import",
        namespace="http://www.ivoa.net/xml/VORegistry/v1.0",
        schemaLocation="http://www.ivoa.net/xml/VORegistry/v1.0",
    )
    oai_xsd.getroot().insert(0, registryinterface_import)
    oai_xsd.getroot().insert(0, voregistry_import)

    oai_schema = etree.XMLSchema(oai_xsd)
    return oai_schema


@pytest.fixture(scope="session")
def voresource_schema():
    # TODO: this method needs to be updated each time a new VO Resource type is
    # added and we may want to explore a solution that isn't so tedious. Perhaps
    # all VO schemas can be autoloaded in the future
    parser = etree.XMLParser()
    parser.resolvers.add(LocalResolver())
    VOR_trav = resources.files("vo_registry") / "static/schemas/VOResource-v1.1.xsd"
    with resources.as_file(VOR_trav) as f:
        voresource_xsd = etree.parse(f.open("rb"), parser=parser)
    registryinterface_import = etree.Element(
        "{http://www.w3.org/2001/XMLSchema}import",
        namespace="http://www.ivoa.net/xml/RegistryInterface/v1.0",
        schemaLocation="http://www.ivoa.net/xml/RegistryInterface/v1.0",
    )
    voregistry_import = etree.Element(
        "{http://www.w3.org/2001/XMLSchema}import",
        namespace="http://www.ivoa.net/xml/VORegistry/v1.0",
        schemaLocation="http://www.ivoa.net/xml/VORegistry/v1.0",
    )
    siaresource_import = etree.Element(
        "{http://www.w3.org/2001/XMLSchema}import",
        namespace="http://www.ivoa.net/xml/SIA/v1.1",
        schemaLocation="http://www.ivoa.net/xml/SIA/v1.1",
    )
    scsresource_import = etree.Element(
        "{http://www.w3.org/2001/XMLSchema}import",
        namespace="http://www.ivoa.net/xml/ConeSearch/v1.0",
        schemaLocation="http://www.ivoa.net/xml/ConeSearch/v1.0",
    )
    voresource_xsd.getroot().insert(0, registryinterface_import)
    voresource_xsd.getroot().insert(0, voregistry_import)
    voresource_xsd.getroot().insert(0, siaresource_import)
    voresource_xsd.getroot().insert(0, scsresource_import)
    voresource_schema = etree.XMLSchema(voresource_xsd)
    return voresource_schema


@pytest.fixture(scope="session")
def oai_dc_schema():
    parser = etree.XMLParser()
    parser.resolvers.add(LocalResolver())

    OAI_trav = resources.files("vo_registry") / "static/schemas/oai_dc.xsd"
    with resources.as_file(OAI_trav) as f:
        oai_dc_xsd = etree.parse(f.open("rb"), parser=parser)

    oai_dc_schema = etree.XMLSchema(oai_dc_xsd)
    return oai_dc_schema
