from lxml import etree

from vo_registry.constants import OAI_NS, MetadataFormats, QParams, Verbs
from vo_registry.resources import ResourceRepo


def listrecords(repo: ResourceRepo, **kwargs: str) -> list[etree._Element]:
    root = etree.Element(f"{{{OAI_NS}}}{Verbs.LIST_RECORDS}")
    mdp = kwargs.get(QParams.METADATA_PREFIX, MetadataFormats.IVO_VOR)
    from_str = kwargs.get(QParams.FROM)
    until_str = kwargs.get(QParams.UNTIL)
    records = repo.get_all(from_str=from_str, until_str=until_str, mdp=mdp)
    for record in records:
        root.append(record)
    return [root]
