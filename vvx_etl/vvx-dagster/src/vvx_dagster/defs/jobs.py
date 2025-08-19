import dagster as dg
from .assets import joined_qppv, vvv_src5

qppv_mods_job = dg.define_asset_job(name="qppv_mods_job", selection=[joined_qppv])
vvv_src5_mods_job = dg.define_asset_job(name="vvv_src5_mods_job", selection=[vvv_src5])
