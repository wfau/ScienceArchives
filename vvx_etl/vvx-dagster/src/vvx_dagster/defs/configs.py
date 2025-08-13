from dataclasses import dataclass


@dataclass
class Config:
    qppv_url: str
    vvv_src5_url: str
    download_dir: str
    n_buckets: int
    columns_to_transform: list[str]


CONFIG = Config(
    qppv_url="http://www-wfau.roe.ac.uk/www-data/VVVXDMP/bulkOut/JoinedQPPV/",
    vvv_src5_url="http://www-wfau.roe.ac.uk/www-data/VVVXDMP/bulkOut/vvvSrc5/",
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
