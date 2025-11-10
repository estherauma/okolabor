from django.utils.translation import get_language
from django.apps import apps
from content.models import AggregatedContent

class StaticContent:
    def __init__(self, language=None):
        raw_lang = (language or (get_language() or 'es-MX').strip().lower())
        self.language = 'es-MX' if raw_lang == 'es-mx' else 'en'
        self._content = None  # Lazy-loaded

    @property
    def content(self):
        if self._content is None:
            self._content = {}
            if apps.ready:
                try:
                    aggregated = AggregatedContent.objects.latest('created_at')
                    if aggregated:
                        self._content = aggregated.content.get(self.language, {})
                except Exception:
                    # Optional: log the exception if necessary
                    pass
        return self._content

    def _normalize(self, value):
        return value.strip().lower().replace(" ", "_").replace("/", "").replace("-", "_")

    def _get_choices(self, section_key):
        data = self.content.get(section_key, {}).get("data", [])
        return [(self._normalize(item["name"]), item["label"]) for item in data]

    def get_label_for_field(self, key, section="form_questions"):
        questions = self.content.get("workExperienceStepTwo", {}).get(section, [])
        for q in questions:
            if q.get("key") == key:
                return q.get("label", key)
        return key

    def get_sector_choices(self):
        return self._get_choices("primaryJobType")

    def get_animal_type_choices(self):
        return self._get_choices("animalTypes")

    def get_crop_type_choices(self):
        return self._get_choices("cropType")

    def get_responsibilities_choices(self, category=None):
        data = self.content.get("responsibilities", {}).get("data", [])
        result = []
        for item in data:
            if not item.get("enabled"):
                continue
            if category and category not in [c.strip() for c in item.get("category", [])]:
                continue
            result.append((self._normalize(item["name"]), item["label"]))
        return result

    def get_animal_responsibilities_choices(self):
        return self.get_responsibilities_choices("Animals")

    def get_crop_responsibilities_choices(self):
        return self.get_responsibilities_choices("Crop and horticulture")

    def get_mechanics_responsibilities_choices(self):
        return self.get_responsibilities_choices("Mechanics")

    def get_worker_supervision_choices(self):
        return self.get_responsibilities_choices("Worker supervision / management")
    
    def get_worker_licensed_vehicle_operation_choices(self):
        return self.get_responsibilities_choices("Licensed vehicle operation")
    
    def get_document_labels(self):
        documents_section = self.content.get("documents", {}).get("form_questions", [])
        return {doc["key"]: doc["label"] for doc in documents_section}
    
    def get_label_for_preference_field(self, key, section="form_questions"):
        questions = self.content.get("workPreferenceStepOne", {}).get(section, [])
        for q in questions:
            if q.get("key") == key:
                return q.get("label", key)
        return key

    def get_options_for_preference_field(self, key, section="form_questions"):
        questions = self.content.get("workPreferenceStepOne", {}).get(section, [])
        for q in questions:
            if q.get("key") == key:
                return q.get("options", [])
        return []
    
    def get_label_for_preference_field_two(self, key, section="form_questions"):
        questions = self.content.get("workPreferenceStepTwo", {}).get(section, [])
        for q in questions:
            if q.get("key") == key:
                return q.get("label", key)
        return key
    
    def get_english_proficiency_options(self):
        questions = self.content.get("profileStepTwo", {}).get("form_questions", [])
        for q in questions:
            if q.get("key") == "englishProficiency":
                return q.get("options", [])
        return []

    def get_english_proficiency_labels(self, key, section="form_questions"):
        questions = self.content.get("profileStepTwo", {}).get(section, [])
        for q in questions:
            if q.get("key") == key:
                return q.get("label") or key
        return key
    
    def get_profile_step_one_label(self, key, section="form_questions"):
        questions = self.content.get("profileStepOne", {}).get(section, [])
        for q in questions:
            if q.get("key") == key:
                return q.get("label") or key
        return key

    def get_add_worker_to_work_request_metadata(self):
        additionalText = self.content.get("rweb-add-worker-to-work-request", {}).get("additional_text", [])
        return additionalText

    def generate_text_variants(self, text):
        """Generate text variants for matching, including normalized and label forms."""
        variants = set()
        variants.add(text)
        normalized_value = self._normalize(text)
        variants.add(normalized_value)
        variants.add(text.lower())
        variants.add(text.upper())
        variants.add(text.title())
        variants.add(text.replace('_', ' '))
        variants.add(text.replace(' ', '_'))
        variants.add(normalized_value.replace('_', ' '))
        variants.add(normalized_value.replace(' ', '_'))
        return {v for v in variants if v}
