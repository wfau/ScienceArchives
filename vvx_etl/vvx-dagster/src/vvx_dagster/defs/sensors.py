import dagster as dg
from .assets import qppv_partitions, vvv_src5_partitions, joined_mods
from .jobs import qppv_mods_job, vvv_src5_mods_job
from ..transformations.extract import get_mods
from .configs import CONFIG


@dg.sensor(job=qppv_mods_job)
def qppv_sensor(context: dg.SensorEvaluationContext):
    all_mods = get_mods(base_url=CONFIG.base_url, table_name="JoinedQPPV")[:10]
    existing = context.instance.get_dynamic_partitions("qppv_mods")
    new_mods = [mod for mod in all_mods if mod not in existing]

    if new_mods:
        return dg.SensorResult(
            run_requests=[dg.RunRequest(partition_key=mod) for mod in new_mods],
            dynamic_partitions_requests=[qppv_partitions.build_add_request(new_mods)],
        )
    return None


@dg.sensor(job=vvv_src5_mods_job)
def vvv_sensor(context: dg.SensorEvaluationContext):
    all_mods = get_mods(base_url=CONFIG.base_url, table_name="vvvSrc5")
    existing = context.instance.get_dynamic_partitions("vvv_src5_mods")
    new_mods = [mod for mod in all_mods if mod not in existing][
        : CONFIG.max_concurrent_runs
    ]

    if new_mods:
        return dg.SensorResult(
            run_requests=[dg.RunRequest(partition_key=mod) for mod in new_mods],
            dynamic_partitions_requests=[
                vvv_src5_partitions.build_add_request(new_mods)
            ],
        )
    return None


@dg.sensor(job=None)  # Attach this to a `source_detection_joined` job if needed
def joined_mods_sensor(context: dg.SensorEvaluationContext):
    qppv = set(context.instance.get_dynamic_partitions("qppv_mods"))
    vvv = set(context.instance.get_dynamic_partitions("vvv_src5_mods"))
    existing = set(context.instance.get_dynamic_partitions("joined_mods"))

    common_mods = qppv.intersection(vvv)
    new_mods = common_mods - existing

    if new_mods:
        return dg.SensorResult(
            run_requests=[dg.RunRequest(partition_key=mod) for mod in new_mods],
            dynamic_partitions_requests=[joined_mods.build_add_request(list(new_mods))],
        )
