# utils.py
from account.models import UserPreference, User
from recruiting.models import WorkAssignment
from django.conf import settings

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

def add_workers_to_shortlist(worker_ids):
    for worker_id in worker_ids:
        worker = User.objects.get(id=worker_id)
        WorkAssignment.objects.create(worker=worker, status='Assigned')
    return True

def get_shortlisted_workers():
    return WorkAssignment.objects.filter(status='Assigned')