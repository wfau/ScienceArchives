import requests
from urllib.robotparser import RobotFileParser


def test_robots(registry_base_url):
    rfp = RobotFileParser()
    rfp.set_url(f"{registry_base_url}/robots.txt")
    rfp.read()
    assert rfp.can_fetch("*", "/index.html")
    assert not rfp.can_fetch("*", "/registry")


def test_landing_page_has_content(registry_base_url):
    r = requests.get(registry_base_url)
    assert r.status_code == 200
    assert "Hello" in str(r.content)
