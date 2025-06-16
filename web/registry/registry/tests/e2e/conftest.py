import os
import requests

import pytest
from lxml import etree

from vo_registry.constants import NS


@pytest.fixture(scope="session")
def registry_base_url():
    """
    The root URL of the service. Usually an origin.
    """
    return os.environ.get("BASE_URL", "http://registry:8080")


@pytest.fixture(scope="session")
def oai_base_url(registry_base_url):
    """
    The root URL of the OAI service
    """
    # this isn't configurable since the registry handler is a hardcoded path
    return f"{registry_base_url}/registry"


# Keeping a hard wall between the registry code and the E2E tests
# So we pull the registry id from the registry, not the code
# a side-benefit of this is that we should be able to run
# the E2E tests against any vo-registry...


@pytest.fixture(scope="session")
def registry_voresource(oai_base_url):
    params = {"verb": "Identify"}
    r = requests.get(oai_base_url, params=params, timeout=5000)
    doc = etree.fromstring(r.content)
    identify_elem = doc[2]
    find_vor = etree.XPath("oai:description/ri:Resource", namespaces=NS)
    return find_vor(identify_elem)[0]


@pytest.fixture(scope="session")
def registry_id(registry_voresource):
    id_elem = registry_voresource.xpath("identifier")[0]
    return id_elem.text


@pytest.fixture(scope="session")
def authority_id(registry_voresource):
    authority = registry_voresource.xpath("managedAuthority")[0].text
    return f"ivo://{authority}"


# Yes, this requires a network connection.
# I'm leaving it like this in case a schema is updated
@pytest.fixture(scope="session")
def oai_schema():
    # TODO: this method needs to be updated each time a new VO Resource type is
    # added and we may want to explore a solution that isn't so tedious. Perhaps
    # all VO schemas can be autoloaded in the future
    parser = etree.XMLParser()
    parser.resolvers.add(HttpsResolver())

    oai_xsd = etree.parse(
        "https://www.openarchives.org/OAI/2.0/OAI-PMH.xsd", parser=parser
    )
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
    oai_dc_import = etree.Element(
        "{http://www.w3.org/2001/XMLSchema}import",
        namespace="http://www.openarchives.org/OAI/2.0/oai_dc/",
        schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/",
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
    oai_xsd.getroot().insert(0, registryinterface_import)
    oai_xsd.getroot().insert(0, voregistry_import)
    oai_xsd.getroot().insert(0, oai_dc_import)
    oai_xsd.getroot().insert(0, siaresource_import)
    oai_xsd.getroot().insert(0, scsresource_import)

    oai_schema = etree.XMLSchema(oai_xsd)
    return oai_schema


class HttpsResolver(etree.Resolver):
    # lxml doesn't support https
    # openarchives moved their files to https
    # so we need to to have our own resolver
    def resolve(self, url, id, context):
        r = requests.get(url, timeout=20000)
        return self.resolve_string(r.content, context)
