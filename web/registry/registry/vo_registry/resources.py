from datetime import datetime
from importlib import resources

from lxml import etree

from vo_registry.errors import IdentifierNotFound
from vo_registry.constants import (
    DC_NS,
    OAI_DC_NS,
    OAI_NS,
    XSI_NS,
    MetadataFormats,
    SetSpecs,
)
from vo_registry.utils import findtext_or_raise, read_xml_from_file, parse_datetime


class VOResource:
    def __init__(self, ivo_vor_root: etree._Element) -> None:
        self.ivo_vor_root = ivo_vor_root
        self.identifier = findtext_or_raise(ivo_vor_root, "identifier")
        self.resource_type = ivo_vor_root.get(f"{{{XSI_NS}}}type")
        self.updated = datetime.strptime(
            ivo_vor_root.get("updated", "updated_missing"), "%Y-%m-%dT%H:%M:%SZ"
        )

    def to_record(self, mdp: str = MetadataFormats.IVO_VOR) -> etree._Element:
        root = etree.Element(f"{{{OAI_NS}}}record")
        header = self.header
        root.append(header)
        if header.get("status") != "deleted":
            metadata = etree.SubElement(root, f"{{{OAI_NS}}}metadata")
            if mdp == MetadataFormats.IVO_VOR:
                metadata.append(self.ivo_vor_root)
            if mdp == MetadataFormats.OAI_DC:
                metadata.append(self.oai_dc_root)
        return root

    @property
    def header(self) -> etree._Element:
        root = etree.Element(f"{{{OAI_NS}}}header")
        if self.ivo_vor_root.get("status") == "deleted":
            root.set("status", "deleted")
        id_element = etree.SubElement(root, f"{{{OAI_NS}}}identifier")
        id_element.text = findtext_or_raise(self.ivo_vor_root, "identifier")
        dt_element = etree.SubElement(root, f"{{{OAI_NS}}}datestamp")
        dt_element.text = self.ivo_vor_root.get("updated")
        setspec_element = etree.SubElement(root, f"{{{OAI_NS}}}setSpec")
        setspec_element.text = SetSpecs.IVO_MANAGED
        return root

    @property
    def oai_dc_root(self) -> etree._Element:
        # "title"       <- title
        # "creator"     <- curation/creator/name (optional, multiple)
        # "subject"     <- content/subject (multiple)
        # "description" <- content/description
        # "publisher"   <- curation/publisher
        # "contributor" <- curation/contributor (optional, multiple)
        # "date"        <- updated
        # "type"        <- xsi:type
        # "format"      unused
        # "identifier"  <- identifier
        # "source"      unused
        # "language"    unused
        # "relation"    unused
        # "coverage"    unused
        # "rights"      unused

        nsmap = {"oai_dc": OAI_DC_NS, "dc": DC_NS}
        root = etree.Element(f"{{{OAI_DC_NS}}}dc", nsmap=nsmap)
        self._add_dc_elems(root, "title", "title")
        self._add_dc_elems(root, "curation/creator/name", "creator")
        self._add_dc_elems(root, "content/subject", "subject")
        self._add_dc_elems(root, "content/description", "description")
        self._add_dc_elems(root, "curation/publisher", "publisher")
        self._add_dc_elems(root, "curation/contributor", "contributor")
        date_elem = etree.SubElement(root, f"{{{DC_NS}}}date")
        date_elem.text = self.ivo_vor_root.get("updated")
        type_elem = etree.SubElement(root, f"{{{DC_NS}}}type")
        type_elem.text = self.resource_type
        self._add_dc_elems(root, "identifier", "identifier")
        return root

    def _add_dc_elems(self, root: etree._Element, xpath: str, tag: str) -> None:
        # we know this will return a list of elements, or empty list
        elems: list[etree._Element] = self.ivo_vor_root.xpath(xpath)  # type: ignore
        for e in elems:
            sub = etree.SubElement(root, f"{{{DC_NS}}}{tag}")
            sub.text = e.text


class ResourceRepo:
    def __init__(self, module: str = "vo_registry", path: str = "resources") -> None:
        self.resources: dict[str, VOResource] = {}
        self.registry_id = ""
        trav = resources.files(module) / f"static/{path}"
        filenames = [path.name for path in list(trav.iterdir())]
        for filename in filenames:
            root = read_xml_from_file(f"{path}/{filename}", module=module)
            resource = VOResource(root)
            if resource.identifier in self.resources:
                raise KeyError(f"Duplicate Identifier: {resource.identifier}")
            self.resources[resource.identifier] = resource
            if resource.resource_type == "vg:Registry":
                self.registry_id = resource.identifier
                self.registry_resource = resource

        datetimes = [r.updated for r in self.resources.values()]
        self.earliest_datetime = min(datetimes)
        self.latest_datetime = max(datetimes)

    def get(
        self, identifier: str, mdp: str = MetadataFormats.IVO_VOR
    ) -> etree._Element:
        resource = self.resources.get(identifier, None)
        if resource is None:
            raise IdentifierNotFound(identifier)
        return resource.to_record(mdp=mdp)

    def get_all(
        self,
        from_str: str | None = None,
        until_str: str | None = None,
        mdp: str = MetadataFormats.IVO_VOR,
    ) -> list[etree._Element]:
        resources = list(self.resources.values())
        if from_str:
            from_datetime = parse_datetime(from_str)
            resources = [r for r in resources if r.updated >= from_datetime]
        if until_str:
            until_datetime = parse_datetime(until_str)
            resources = [r for r in resources if r.updated <= until_datetime]
        return [r.to_record(mdp=mdp) for r in resources]
