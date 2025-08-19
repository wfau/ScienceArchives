from .defs.resources import SparkResource
from dagster import (
    Definitions,
    load_assets_from_modules,
    load_asset_checks_from_modules,
)
from .defs import assets, asset_checks, sensors, jobs

loaded_assets = load_assets_from_modules([assets])
loaded_checks = load_asset_checks_from_modules([asset_checks])
loaded_jobs = [jobs.vvv_src5_mods_job, jobs.qppv_mods_job]
loaded_sensors = [sensors.vvv_sensor, sensors.qppv_sensor]

defs = Definitions(
    assets=loaded_assets,
    asset_checks=loaded_checks,
    jobs=loaded_jobs,
    sensors=loaded_sensors,
    resources={
        "spark": SparkResource(
            metastore_uri="/tmp/metastore_db",
            warehouse_dir="/tmp/warehouse",
            cores=4,
            memory="16g",
        )
    },
)
