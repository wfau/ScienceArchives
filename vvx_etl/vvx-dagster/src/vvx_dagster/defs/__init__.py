# from dagster import Definitions
# from .resources import spark
# from .assets import (
#     detection_array_valued_bucketed,
#     source_bucketed,
#     source_correctly_bucketed,
#     detection_correctly_bucketed,
#     source_detection_joined_correctly_bucketed,
#     source_detection_joined_matches_schema,
#     detection_and_joined_consistent_rows,
# )

# defs = Definitions(
#     assets=[
#         detection_array_valued_bucketed,
#         source_bucketed,
#         source_correctly_bucketed,
#         detection_correctly_bucketed,
#         source_detection_joined_correctly_bucketed,
#         source_detection_joined_matches_schema,
#         detection_and_joined_consistent_rows,
#     ],
#     resources={"spark": spark},
# )
