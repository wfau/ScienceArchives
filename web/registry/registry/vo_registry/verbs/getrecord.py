from lxml import etree

from vo_registry.constants import OAI_NS, MetadataFormats, QParams, Verbs
from vo_registry.resources import ResourceRepo


def getrecord(repo: ResourceRepo, **kwargs: str) -> list[etree._Element]:
    root = etree.Element(f"{{{OAI_NS}}}{Verbs.GET_RECORD}")
    identifier = kwargs[QParams.IDENTIFIER]
    mdp = kwargs.get(QParams.METADATA_PREFIX, MetadataFormats.IVO_VOR)
    record = repo.get(identifier, mdp=mdp)
    root.append(record)
    return [root]
