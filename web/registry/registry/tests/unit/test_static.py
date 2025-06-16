from importlib import resources

from lxml import etree

from vo_registry.resources import ResourceRepo
from vo_registry.utils import read_xml_from_file


def test_voresource_files_are_valid(voresource_schema):
    trav = resources.files("vo_registry") / "static/resources"
    filenames = [path.name for path in list(trav.iterdir())]
    for filename in filenames:
        root = read_xml_from_file(f"resources/{filename}")
        try:
            voresource_schema.assertValid(root)
        except etree.DocumentInvalid as exc:  # pragma: no cover
            raise ValueError(f"File: static/resources/{filename} is invalid") from exc

    # if we get here, all the resources are valid


def test_can_create_resource_repo():
    # this will detect duplicate identifiers
    ResourceRepo()
