from .defs.resources import SparkResource
from dagster import (
    Definitions,
    load_assets_from_modules,
    load_asset_checks_from_modules,
)
from .defs import assets, asset_checks

loaded_assets = load_assets_from_modules([assets])
loaded_checks = load_asset_checks_from_modules([asset_checks])

defs = Definitions(
    assets=loaded_assets,
    asset_checks=loaded_checks,
    resources={
        "spark": SparkResource(
            metastore_uri="/tmp/metastore_db",
            warehouse_dir="/tmp/warehouse",
            cores=4,
            memory="16g",
        )
    },
)
