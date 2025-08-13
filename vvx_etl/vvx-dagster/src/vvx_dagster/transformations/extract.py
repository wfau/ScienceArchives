import requests
from bs4 import BeautifulSoup
from pathlib import Path


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


def get_parquet_urls(url: str) -> list[str]:
    """Get list of paths from URL"""

    parquets = []
    moduli = scrape_for_files(url=url, keyword="mod")
    for mod_url in moduli:
        parquets_in_mod = scrape_for_files(mod_url, "parquet")
        parquets.extend(parquets_in_mod)

    return parquets


def download_parquets(url: str, output_path: str) -> None:
    parquet_urls = get_parquet_urls(url)
    base_url = "http://www-wfau.roe.ac.uk/www-data/VVVXDMP/bulkOut/"  # need to change this - shouldn't be hardcoded

    print(parquet_urls)

    for url in parquet_urls[0:2]:
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
