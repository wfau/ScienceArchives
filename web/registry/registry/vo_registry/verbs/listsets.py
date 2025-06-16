from lxml import etree

from vo_registry.constants import OAI_NS, SetSpecs, Verbs
from vo_registry.resources import ResourceRepo


def listsets(repo: ResourceRepo, **kwargs: str) -> list[etree._Element]:
    root = etree.Element(f"{{{OAI_NS}}}{Verbs.LIST_SETS}")
    set_child = etree.SubElement(root, f"{{{OAI_NS}}}set")
    etree.SubElement(set_child, f"{{{OAI_NS}}}setSpec").text = SetSpecs.IVO_MANAGED
    etree.SubElement(set_child, f"{{{OAI_NS}}}setName").text = SetSpecs.IVO_MANAGED
    return [root]
