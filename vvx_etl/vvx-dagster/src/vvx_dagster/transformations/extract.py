import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin


def scrape_for_files(url: str, keyword: str) -> list[str]:
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    res = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and keyword in href:
            res.append(url + href)
    return res


def get_mods(base_url: str, table_name: str) -> list[str]:
    """Get list of mods of a table"""
    url = urljoin(base_url + "/", table_name + "/")
    moduli = scrape_for_files(url=url, keyword="mod")
    return [mod_url.replace(url, "").replace("/", "") for mod_url in moduli]


def get_parquet_urls(url: str) -> list[str]:
    """Get list of paths from URL"""

    parquets = []
    moduli = scrape_for_files(url=url, keyword="mod")
    for mod_url in moduli:
        parquets_in_mod = scrape_for_files(mod_url, "parquet")
        parquets.extend(parquets_in_mod)

    return parquets


def download_parquets(
    base_url: str, table_name: str, mod: str, output_path: str
) -> None:
    url = urljoin(base_url + "/", table_name + "/" + mod + "/")
    parquet_urls = get_parquet_urls(url)

    for url in parquet_urls:
        relative_path = url.replace(base_url, "")
        out_path = Path(output_path) / relative_path

        if out_path.name == "":
            raise ValueError(f"No filename in URL: {url}")

        out_path.parent.mkdir(exist_ok=True, parents=True)

        print(f"Downloading {url} -> {out_path}")
        r = requests.get(url)
        r.raise_for_status()

        with open(out_path, "wb") as f:
            f.write(r.content)
