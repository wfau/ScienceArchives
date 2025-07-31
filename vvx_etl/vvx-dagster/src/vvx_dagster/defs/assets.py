import dagster as dg
from bs4 import BeautifulSoup
import requests
from pathlib import Path
from ..transformations.array_columns import make_array_cols
import pandas as pd
from dagster import asset, AssetExecutionContext
from .resources import spark

DESTINATION = "/home/sharnqvi/VVVNewDataModel/dagster_downloads_temp"


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
    base_url = "http://www-wfau.roe.ac.uk/www-data/VVVXDMP/bulkOut/"

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


@dg.asset
def joined_qppv() -> None:
    source_path = "http://www-wfau.roe.ac.uk/www-data/VVVXDMP/bulkOut/JoinedQPPV/"
    destination_path = DESTINATION

    download_parquets(url=source_path, output_path=destination_path)


@dg.asset
def vvv_src5() -> None:
    source_path = "http://www-wfau.roe.ac.uk/www-data/VVVXDMP/bulkOut/vvvSrc5/"
    destination_path = DESTINATION

    download_parquets(url=source_path, output_path=destination_path)


@dg.asset
def vvv_var() -> None:
    source_path = "http://www-wfau.roe.ac.uk/www-data/VVVXDMP/bulkOut/vvvVar/"
    destination_path = DESTINATION

    download_parquets(url=source_path, output_path=destination_path)


@dg.asset
def vvv_x_gaia() -> None:
    source_path = "http://www-wfau.roe.ac.uk/www-data/VVVXDMP/bulkOut/vvvXgaia/"
    destination_path = DESTINATION

    download_parquets(url=source_path, output_path=destination_path)


@dg.asset(deps=["joined_qppv"], required_resource_keys={"spark"})
def detection_array_valued(context: AssetExecutionContext):
    spark = context.resources.spark.spark_session

    detection_df = spark.read.parquet(DESTINATION + "/JoinedQPPV/mod0000")
    columns_to_array_value = [
        "mjd",
        "aperMag1",
        "aperMag1err",
        "aperMag2",
        "aperMag2err",
        "aperMag3",
        "aperMag3err",
        "errBits",
        "averageConf",
        "class",
        "classStat",
        "deprecated",
        "ppErrBits",
        "objID",
        "multiframeID",
        "extNum",
        "seqNum",
        "flag",
        "modelDistSecs",
    ]
    detection_arrayvals_df = make_array_cols(
        detection_df,
        key="sourceID",
        filter_col="filterID",
        order_by="sourceID",
        cols_to_transform=columns_to_array_value,
    )
