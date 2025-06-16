from importlib import resources

from lxml import etree


def test_can_load_all_xml_files():
    travs = [resources.files("vo_registry") / "static/"]
    while travs:
        trav = travs.pop()
        files = [path for path in trav.iterdir() if path.is_file()]
        travs += [path for path in trav.iterdir() if path.is_dir()]
        for f in files:
            with resources.as_file(f) as f:
                xml_string = f.open("rb").read()
                etree.fromstring(xml_string)
    # if we get here, they are all parsable
