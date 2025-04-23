from django.utils.translation import get_language
from content.models import AggregatedContent

class StaticContent:
    def __init__(self):
        raw_lang = get_language().strip().lower()
        self.language = 'es-MX' if raw_lang == 'es-mx' else 'en'
        self.content = {}
        aggregated = AggregatedContent.objects.first()
        if aggregated:
            self.content = aggregated.content.get(self.language, {})

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
            if category and category not in item.get("category", []):
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
    
    def get_document_labels(self):
        documents_section = self.content.get("documents", {}).get("form_questions", [])
        return {doc["key"]: doc["label"] for doc in documents_section}
