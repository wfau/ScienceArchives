from lxml import etree

from vo_registry.constants import OAI_NS, MetadataFormats, Verbs
from vo_registry.resources import ResourceRepo


def listmetadataformats(repo: ResourceRepo, **kwargs: str) -> list[etree._Element]:
    formats = [
        (
            MetadataFormats.IVO_VOR,
            "http://www.ivoa.net/xml/VOResource/v1.0",
            "http://www.ivoa.net/xml/VOResource/v1.0",
        ),
        (
            MetadataFormats.OAI_DC,
            "http://www.openarchives.org/OAI/2.0/oai_dc.xsd",
            "http://www.openarchives.org/OAI/2.0/oai_dc/",
        ),
    ]
    root = etree.Element(f"{{{OAI_NS}}}{Verbs.LIST_METADATA_FORMATS}")
    for f in formats:
        child = etree.SubElement(root, f"{{{OAI_NS}}}metadataFormat")
        etree.SubElement(child, f"{{{OAI_NS}}}metadataPrefix").text = f[0]
        etree.SubElement(child, f"{{{OAI_NS}}}schema").text = f[1]
        etree.SubElement(child, f"{{{OAI_NS}}}metadataNamespace").text = f[2]
    return [root]
