# utils.py
from account.models import UserPreference, User
from recruiting.models import WorkAssignment
from django.conf import settings
from django.contrib import messages

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
    added_any = False
    already_assigned = []
    for worker_id in worker_ids:
        worker = User.objects.get(id=worker_id)
        latest_assignment = WorkAssignment.objects.filter(worker=worker).order_by('-assigned_date').first()
        if latest_assignment and latest_assignment.status in ['offersent', 'confirmed', 'assigned']:
            already_assigned.append(worker.first_name + " " + worker.last_name)
            continue
        WorkAssignment.objects.filter(worker=worker, status='cancelled').delete()
        WorkAssignment.objects.create(worker=worker, status='assigned')
        added_any = True
    return added_any, already_assigned



def get_shortlisted_workers(status='assigned'):
    return WorkAssignment.objects.filter(status=status)
