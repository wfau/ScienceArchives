from lxml import etree

from vo_registry.constants import OAI_NS, Verbs, QParams
from vo_registry.resources import ResourceRepo


def listidentifiers(repo: ResourceRepo, **kwargs: str) -> list[etree._Element]:
    root = etree.Element(f"{{{OAI_NS}}}{Verbs.LIST_IDENTIFIERS}")
    headers = [
        r[0]
        for r in repo.get_all(
            from_str=kwargs.get(QParams.FROM), until_str=kwargs.get(QParams.UNTIL)
        )
    ]
    for header in headers:
        root.append(header)
    return [root]
