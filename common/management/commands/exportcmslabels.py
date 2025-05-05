import os
import polib
from django.core.management.base import BaseCommand
from content.models import AggregatedContent

class Command(BaseCommand):
    help = 'Export CMS additionalText labels to .po files for English and Spanish'

    def handle(self, *args, **options):
        aggregated = AggregatedContent.objects.first()
        if not aggregated:
            self.stdout.write(self.style.ERROR('No AggregatedContent found'))
            return

        content = aggregated.content

        translations = {
            'en': {},
            'es-MX': {}
        }

        for lang_code, pages in content.items():
            if lang_code not in translations:
                continue 

            for page_key, page_data in pages.items():
                if not page_key.startswith('rweb-'):
                    continue

                additional_text = page_data.get('additionalText', [])
                for item in additional_text:
                    key = item.get('key')
                    value = item.get('value')

                    if not key or not value:
                        continue

                    translations[lang_code][key] = value

        self.update_po_file('en', translations['en'])
        self.update_po_file('es_MX', translations['es-MX'])

        self.stdout.write(self.style.SUCCESS('CMS Labels Exported Successfully'))

    def update_po_file(self, language_code, translations):
        po_path = f'locale/{language_code}/LC_MESSAGES/django.po'

        if not os.path.exists(po_path):
            self.stdout.write(self.style.ERROR(f'{po_path} does not exist'))
            return

        po = polib.pofile(po_path)
        updated_keys = []

        for key, value in translations.items():
            entry = po.find(key)
            if entry:
                entry.msgstr = value
                updated_keys.append(key)

        if updated_keys:
            po.save(po_path)
            self.stdout.write(self.style.SUCCESS(f'Updated {len(updated_keys)} keys in {po_path}'))
        else:
            self.stdout.write(self.style.WARNING(f'No matching keys found in {po_path}. No changes made.'))

