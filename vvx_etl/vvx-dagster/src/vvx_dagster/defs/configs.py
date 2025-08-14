from dataclasses import dataclass


@dataclass
class Config:
    base_url: str
    download_dir: str
    n_buckets: int
    columns_to_transform: list[str]


CONFIG = Config(
    base_url="http://www-wfau.roe.ac.uk/www-data/VVVXDMP/bulkOut/",
    download_dir="~/VVVNewDataModel/dagster_downloads_temp",
    n_buckets=10,
    columns_to_transform=[
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
    ],
)
