from datetime import datetime, timezone

from lxml import etree
from lxml.etree import _Element, _ElementTree
from starlette.datastructures import QueryParams

from vo_registry.constants import OAI_NS, XSI_NS


def oai_wrap(children: list[_Element], params: QueryParams, url: str) -> _ElementTree:
    nsmap = {None: OAI_NS, "xsi": XSI_NS}
    root = etree.Element(f"{{{OAI_NS}}}OAI-PMH", nsmap=nsmap)  # type: ignore
    root.set(
        f"{{{XSI_NS}}}schemaLocation",
        f"{OAI_NS} https://www.openarchives.org/OAI/2.0/OAI-PMH.xsd",
    )
    date_child = etree.SubElement(root, f"{{{OAI_NS}}}responseDate")
    date_child.text = datetime.now(timezone.utc).isoformat()
    request_child = etree.SubElement(root, f"{{{OAI_NS}}}request")
    request_child.text = url
    if children[0].tag != f"{{{OAI_NS}}}error":
        for key, value in params.items():
            request_child.set(key, value)
    for child in children:
        root.append(child)
    return root.getroottree()
