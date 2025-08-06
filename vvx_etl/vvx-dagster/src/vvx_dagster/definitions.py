# src/vvx_dagster/definitions.py

from dagster import (
    Definitions,
    load_assets_from_modules,
    load_asset_checks_from_modules,
)
from .defs.resources import spark
from .defs import assets, asset_checks

loaded_assets = load_assets_from_modules([assets])
loaded_checks = load_asset_checks_from_modules([asset_checks])

resources = {"spark": spark}

defs = Definitions(
    assets=loaded_assets, asset_checks=loaded_checks, resources=resources
)
