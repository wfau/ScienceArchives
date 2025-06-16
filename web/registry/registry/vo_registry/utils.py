import json
import yaml
from datetime import datetime
from importlib import resources

import xmltodict
from lxml import etree


def read_xml_from_file(filename: str, module: str = "vo_registry") -> etree._Element:
    """
    Loads data from a file and returns XML representation. XML files are
    preferred but this also supports .json and .yaml file (results may vary).
    """
    trav = resources.files(module) / f"static/{filename}"
    with resources.as_file(trav) as f:
        content_string = f.open("rb").read()
    if filename.endswith(".json"):
        # NOTE: JSON is an unordered data structure, so there is not guaranteed
        # to work. Python >3.7 does maintain order in dicts, and xmltodict does
        # respect that and json.loads _should_ maintain order, but using xml
        # directly is always safer
        content_dict = json.loads(content_string)
        content_string = bytes(xmltodict.unparse(content_dict), "utf-8")
    if filename.endswith(".yaml"):
        content_dict = yaml.safe_load(content_string)
        content_string = bytes(xmltodict.unparse(content_dict), "utf-8")
    return etree.fromstring(content_string)


def parse_datetime(text: str) -> datetime:
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise ValueError("no valid date format found")


def findtext_or_raise(element: etree._Element, path: str) -> str:
    if text := element.findtext(path):
        return text
    else:
        raise ValueError(f"path {path} has no text")
