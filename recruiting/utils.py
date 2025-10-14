# utils.py
from account.models import UserPreference, User
from common.logger import AppLogger
from recruiting.models import WorkAssignment
from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404
from recruiting.models import WorkRequests, Role
from content.models import AggregatedContent
from django.utils.translation import get_language
from datetime import date
from django.utils import timezone
from django.db import transaction
from recruiting.models import WorkRequests, Role, WorkAssignment, OkoMessage


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
        """Fetch town, work experience, proficiency, and location preference from UserPreference"""
        preference_keys = ["Town", "workExperienceList", "level", "whereYouWantToWork"]
        preferences = UserPreference.objects.filter(user=user, key__in=preference_keys).values("key", "value")
        worker_details = {pref["key"]: pref["value"] for pref in preferences}
        return {
            "town": worker_details.get("Town"),
            "work_experience": worker_details.get("workExperienceList", "Not Provided"),
            "english_proficiency": worker_details.get("level", "Not Provided"),
            "location_preference": worker_details.get("whereYouWantToWork", "Not Provided"),
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
        return []
    
def calculate_total_experience(user):
    # Calculate total work experience in years based on filters. 
    # Right now we aren't factoring in filters, just summing all experiences.
    experiences = user.work_experiences.all()
    total_months = 0
    for exp in experiences:
        value = exp.approx_total_months_worked
        if isinstance(value, (int, float)):
            total_months += value
        elif isinstance(value, str):
            try:
                total_months += float(value)
            except ValueError:
                pass
    return round(total_months)

def calculate_months_ofH2A_expererience(user):
    experiences = user.work_experiences.filter(work_under_h2a_in_usa='No')
    total_months = 0
    for exp in experiences:
        value = exp.approx_total_months_worked
        if isinstance(value, (int, float)):
            total_months += value
        elif isinstance(value, str):
            try:
                total_months += float(value)
            except ValueError:
                pass
    return round(total_months)


@transaction.atomic
def duplicate_work_request(original_request, new_name, new_start_date, new_end_date):
    new_request = WorkRequests.objects.create(
        name=new_name,
        start_date=new_start_date,
        end_date=new_end_date,
        required_workers=original_request.required_workers,
        employer=original_request.employer,
        status='Draft'
    )

    role_mapping = {}
    for role in original_request.roles.all():
        new_role = Role.objects.create(
            title=role.title,
            usdol_case_number=role.usdol_case_number,
            number_of_required_workers=role.number_of_required_workers,
            description=role.description,
            work_type=role.work_type,
            work_type_detail=role.work_type_detail,
            responsibilities_types=role.responsibilities_types,
            work_request=new_request
        )
        role_mapping[role.id] = new_role

    for assignment in original_request.assignments.all():
        if assignment.worker and assignment.role_id in role_mapping:
            WorkAssignment.objects.create(
                work_request=new_request,
                role=role_mapping[assignment.role_id],
                worker=assignment.worker,
                status='shortlisted'
            )

    for msg in original_request.messages.all():
        OkoMessage.objects.create(
            recipient_type=msg.recipient_type,
            job_order=new_request,
            include_recipients=msg.include_recipients,
            subject=msg.subject,
            body=msg.body,
            auto_reply=msg.auto_reply
        )

    return new_request
