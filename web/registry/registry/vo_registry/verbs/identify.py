import os
from lxml import etree

from vo_registry.constants import OAI_NS
from vo_registry.resources import ResourceRepo
from vo_registry.utils import read_xml_from_file


def identify(repo: ResourceRepo, **kwargs: str) -> list[etree._Element]:
    root = read_xml_from_file("identify.xml")
    registry_root = repo.registry_resource.ivo_vor_root
    repo_name = registry_root.findtext("title")
    base_url = f"{os.environ.get('BASE_URL')}/registry"
    admin_email = registry_root.findtext("curation/contact/email")
    earliest_datestamp = repo.earliest_datetime.isoformat(timespec="seconds") + "Z"

    # This is going to become the construction of the identify elements
    next(root.iter(f"{{{OAI_NS}}}repositoryName")).text = repo_name
    next(root.iter(f"{{{OAI_NS}}}baseURL")).text = base_url
    next(root.iter(f"{{{OAI_NS}}}adminEmail")).text = admin_email
    next(root.iter(f"{{{OAI_NS}}}earliestDatestamp")).text = earliest_datestamp

    description = next(root.iter(f"{{{OAI_NS}}}description"))
    description.append(registry_root)

    return [root]
