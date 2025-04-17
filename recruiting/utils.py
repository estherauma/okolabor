# utils.py
from account.models import UserPreference, User
from recruiting.models import WorkAssignment
from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404
from recruiting.models import WorkRequests, Role
from content.models import AggregatedContent
from django.utils.translation import get_language


ONBOARDING_STEPS = [
    "profileStepOne",
    "workExperienceList",
    "documentsStepOne",
    "levelOfProficiency",
    "recordVideo",
    "workPreferenceStepOne",
    "workPreferenceStepTwo"
]

def calculate_profile_completion(user):
    user_preferences = UserPreference.objects.filter(user=user, key__in=ONBOARDING_STEPS)
    user_prefs_dict = {pref.key: pref.value.lower() == "true" for pref in user_preferences}
    completed_steps = sum(user_prefs_dict.get(step, False) for step in ONBOARDING_STEPS)
    total_steps = len(ONBOARDING_STEPS)
    return round((completed_steps / total_steps) * 100, 2) if total_steps > 0 else 0

def get_worker_preferences(user):
    preference_keys = ["town", "workExperienceList", "levelOfProficiency", "locationPreference"]
    preferences = UserPreference.objects.filter(user=user, key__in=preference_keys).values("key", "value")
    worker_details = {pref["key"]: pref["value"] for pref in preferences}
    return {
        "town": worker_details.get("town", "Not Provided"),
        "work_experience": worker_details.get("workExperienceList", "Not Provided"),
        "english_proficiency": worker_details.get("levelOfProficiency", "Not Provided"),
        "location_preference": worker_details.get("locationPreference", "Not Provided"),
    }


def add_workers_to_shortlist(worker_ids, work_request_id, role_id):
    added_any = False
    already_assigned = []
    work_request = get_object_or_404(WorkRequests, pk=work_request_id)
    role = get_object_or_404(Role, pk=role_id)

    for worker_id in worker_ids:
        worker = get_object_or_404(User, pk=worker_id)

        # Check if the worker is already assigned to the same role in the same work request
        existing_assignment = WorkAssignment.objects.filter(
            worker=worker,
            work_request=work_request,
            role=role,
            status__in=['offersent', 'confirmed', 'assigned']
        ).first()

        if existing_assignment:
            already_assigned.append(worker.first_name + " " + worker.last_name)
            continue

        # Delete any cancelled assignments for the worker in the same work request and role
        WorkAssignment.objects.filter(
            worker=worker,
            work_request=work_request,
            role=role,
            status='cancelled'
        ).delete()

        # Create a new WorkAssignment with the role and work_request properly set
        WorkAssignment.objects.create(
            work_request=work_request,
            role=role,
            worker=worker,
            status='assigned'
        )
        added_any = True

    return added_any, already_assigned

def get_shortlisted_workers(status, role_id):
    return WorkAssignment.objects.filter(
        status=status,
        role_id=role_id
    ).select_related('worker')



def get_sector_choices():
    raw_lang = get_language().strip().lower()
    language = 'es-MX' if raw_lang == 'es-mx' else 'en'

    try:
        aggregated = AggregatedContent.objects.first()
        job_data = aggregated.content.get(language, {}).get("primaryJobType", {}).get("data", [])

        choices = []
        for item in job_data:
            value = item["name"].strip().lower().replace(" ", "_").replace("/", "").replace("-", "_")
            label = item["label"]
            choices.append((value, label))

        return choices
    except Exception as e:
        print("[get_sector_choices] Error:", e)
        return []

def get_animal_type_choices():
    raw_lang = get_language().strip().lower()
    language = 'es-MX' if raw_lang == 'es-mx' else 'en'

    try:
        aggregated = AggregatedContent.objects.first()
        if not aggregated:
            return []

        animal_data = aggregated.content.get(language, {}).get("animalTypes", {}).get("data", [])

        choices = []
        for item in animal_data:
            value = item["name"].strip().lower().replace(" ", "_").replace("/", "").replace("-", "_")
            label = item["label"]
            choices.append((value, label))

        return choices
    except Exception as e:
        print("[get_animal_type_choices] Error:", e)
        return []
    
def get_responsibilities_choices(category=None):
    from django.utils.translation import get_language

    raw_lang = get_language().strip().lower()
    language = 'es-MX' if raw_lang == 'es-mx' else 'en'

    try:
        aggregated = AggregatedContent.objects.first()
        if not aggregated:
            return []

        all_data = aggregated.content.get(language, {}).get("responsibilities", {}).get("data", [])
        choices = []

        for item in all_data:
            if not item.get("enabled", False):
                continue 

            categories = item.get("category", [])
            if category and category not in categories:
                continue 

            value = item["name"].strip().lower().replace(" ", "_").replace("/", "").replace("-", "_")
            label = item["label"]
            choices.append((value, label))

        return choices
    except Exception as e:
        return []

def get_crop_type_choices():
    raw_lang = get_language().strip().lower()
    language = 'es-MX' if raw_lang == 'es-mx' else 'en'

    try:
        aggregated = AggregatedContent.objects.first()
        if not aggregated:
            return []

        animal_data = aggregated.content.get(language, {}).get("cropType", {}).get("data", [])

        choices = []
        for item in animal_data:
            value = item["name"].strip().lower().replace(" ", "_").replace("/", "").replace("-", "_")
            label = item["label"]
            choices.append((value, label))

        return choices
    except Exception as e:
        return []
    
def get_animal_responsibilities_choices():
    return get_responsibilities_choices(category="Animals")

def get_mechanics_responsibilities_choices():
    return get_responsibilities_choices(category="Mechanics")

def get_crop_responsibilities_choices():
    return get_responsibilities_choices(category="Crop and horticulture")

def get_licensed_vehicle_choices():
    return get_responsibilities_choices(category="Licensed vehicle operation ")

def get_construction_responsibilities_choices():
    return get_responsibilities_choices(category="Construction")

def get_worker_supervision_choices():
    return get_responsibilities_choices(category="Worker supervision / management")
    
