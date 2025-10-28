from django import template
from urllib.parse import urlencode

register = template.Library()


@register.simple_tag
def get_workers_page_params(**kwargs):
    params = {}
    role = kwargs.get("role")
    dynamic_fields_keys = {
        "animals": {
            "type_details_key": "animal_types",
            "responsibilities_key": "responsibilities_types",
            "label": "Animals",
        },
        "crop_and_horticulture": {
            "type_details_key": "crop_types",
            "responsibilities_key": "crop_job_types",
            "label": "Crop and Horticulture",
        },
        "mechanics": {
            "responsibilities_key": "mechanic_job_types",
            "label": "Mechanics",
        },
        "worker_supervision": {
            "responsibilities_key": "supervision_jobs_types",
            "label": "Worker Supervision/Management",
        },
        "licensed_vehicle_operation": {
            "responsibilities_key": "licensed_vehicle_operation_types",
            "label": "Licensed Vehicle Operation",
        },
        "other": {
            "label": "Other",
        },
    }
    if role:
        params["role"] = getattr(role, "id")
        params["work_request"] = getattr(role, "work_request_id")
        work_type_details = getattr(role, "work_type_detail", None)

        if hasattr(role, "work_type"):
            work_type = getattr(role, "work_type")
            params["type_sector"] = dynamic_fields_keys.get(work_type, dynamic_fields_keys["other"]).get("label")
        if work_type_details:
            work_type_keys = dynamic_fields_keys.get(getattr(role, "work_type"), None)
            if work_type_keys:
                details_key = work_type_keys.get("type_details_key", None)
                responsibilities_key = work_type_keys.get("responsibilities_key")
                if details_key:
                    details = work_type_details.get(details_key, [])
                    for item in details:
                        params["dynamic_field_1"] = item
                if responsibilities_key:
                    responsibilities = work_type_details.get(responsibilities_key, [])
                    for item in responsibilities:
                        params["dynamic_field_2"] = item

    if params:
        return "?" + urlencode(params)
    return ""
