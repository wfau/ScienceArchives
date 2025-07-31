from dagster import Definitions
from .resources import spark
from .assets import detection_array_valued

defs = Definitions(assets=[detection_array_valued], resources={"spark": spark})
