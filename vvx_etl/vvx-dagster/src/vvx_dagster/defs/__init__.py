from dagster import Definitions
from .resources import spark
from .assets import detection_array_valued_bucketed, source_bucketed

defs = Definitions(
    assets=[detection_array_valued_bucketed, source_bucketed],
    resources={"spark": spark},
)
