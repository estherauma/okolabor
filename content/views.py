from decouple import config
from django.utils.dateparse import parse_datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import re

from content.models import AggregatedContent
from content.serializers import AggregatedContentSerializer


class ContentAPI():
    def __init__(self) -> None:
        self.api_url = config('CMS_API_URL')
        self.access_token = config('CMS_API_TOKEN')
        self.headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
        self.languages = []
        self.start_content_fetch()
        self.documents = {}
       
    def start_content_fetch(self):
        try:
            response = requests.get(self.api_url, headers=self.headers)
            self.content = response.json()
            self.languages = self.content['locales']
            self.documents = self.start_document_fetch()
        except requests.RequestException as e:
            return {
                "error": str(e)
            }
        except ValueError as e:
            print("Error: ", e)

    def start_document_fetch(self):
        documents = {}
        for language in self.languages:
            url = f"{self.api_url}?locale={language['code']}"
            language_docs = requests.get(url, headers=self.headers).json()
            documents[language['code']] = self.aggregate_content(language_docs)
        # save content to the database
        aggregated_content = AggregatedContent()
        aggregated_content.content = documents
        aggregated_content.save()
        return documents

    def aggregate_content(self, lang_content):
        aggregated_content = {}
        aggregated_content['languages'] = self.languages
        
        def aggregate_form_questions(form_qn_data):
            question_data = []
            additional_text = []
            for item in form_qn_data['dynamic_zone']:
                if item['__component'] == 'okolabor.form-questions':
                    question_options = []
                    if item['Options'] and item['OptionTranslations']:
                        question_options = generate_select_options(
                            item['Options'], item['OptionTranslations'])
                    question_data.append({
                        'key': item['Key'],
                        'label': item['Label'],
                        'category': item['Category'],
                        'help_text': item['HelpText'],
                        'required': item['Required'],
                        'placeholder': item['Placeholder'],
                        'question_type': item['QuestionType'],
                        'options': question_options
                    })

                if item['__component'] == 'okolabor.additional-text':
                    additional_text = aggregate_key_value_text(
                        item['repeatable_zone']
                    )
            return question_data, additional_text

        def aggregate_key_value_text(common_text_data):
            common_texts = []
            for item in common_text_data:
                common_texts.append({
                    'key': item['key'],
                    'value': item['value']
                })
            return common_texts

        def generate_select_options(options, options_translations):
            options = re.split(r',\s*|\s*,\s*', options)
            options_translations = re.split(
                r',\s*|\s*,\s*', options_translations)
            final_options_array = [
                    {"value": value, "label": key}
                    for key, value in zip(options_translations, options)
            ]
            return final_options_array
        
        def aggregate_menu_content(menu_content_data):
            menu_content = []
            for item in menu_content_data:
                menu_content.append({
                    'url': item.get('Url', None),
                    'icon': item.get('Icon', None),
                    'title': item.get('Title', None),
                    'enabled': item.get('Enabled', None),
                    'label': item.get('Label(Translate)', None),
                    'order': item.get('Order', None),
                })
            return menu_content

        for item in lang_content['data']:
            if item['custom_type'] == 'form_questions':
                aggregation_response = aggregate_form_questions(item)
                page_data = {
                    'page_id': item['id'],
                    'page_title': item['page_title'],
                    'preview_title': item['preview_title'],
                    'form_questions': aggregation_response[0],
                    'additional_text': aggregation_response[1]
                }
                aggregated_content[item['page_id']] = page_data

            if item['custom_type'] == 'common_text':
                aggregation_response = aggregate_key_value_text(
                    item['dynamic_zone'])
                page_data = {
                    'page_id': item['page_id'],
                    'page_title': item['page_title'],
                    'preview_title': item['preview_title'],
                    'data': aggregation_response
                }
                aggregated_content[item['page_id']] = page_data
            
            if item['custom_type'] == 'menu_content':
                aggregation_response = aggregate_menu_content(item['dynamic_zone'])
                page_data = {
                    'page_id': item['page_id'],
                    'page_title': item['page_title'],
                    'preview_title': item['preview_title'],
                    'last_updated': item['last_published_at'],
                    'data': aggregation_response
                }
                aggregated_content[item['page_id']] = page_data
        return aggregated_content


class AggregatedContentView(APIView):
    def get(self, request):
        try:
            latest = AggregatedContent.objects.latest('created_at')
            serializer = AggregatedContentSerializer(latest, many=False)
            return Response({
                'data': [serializer.data],
                'error_messages': []
            }, status.HTTP_200_OK)
        except AggregatedContent.DoesNotExist:
            return Response({}, status.HTTP_200_OK)


class StartContentAggregation(APIView):
    def get(self, request):
        api = ContentAPI()
        documents = api.start_content_fetch()
        return Response(documents, status.HTTP_200_OK)


class ContentUpdateView(APIView):
    # ToDo: Set up workflow for webhooks
    def post(self, request):
        return Response({}, status.HTTP_200_OK)


class CompareContent(APIView):
    def get(self, request):
        app_content_created_at = request.query_params.get(
            'app_content_created_at'
        )
        parsed_app_content_created_at = parse_datetime(app_content_created_at)
        latest_content = AggregatedContent.objects.order_by(
            '-created_at')[:1].get()
        serializer = AggregatedContentSerializer(latest_content, many=False)
        latest_content_created_at = parse_datetime(
            serializer.data['created_at']
        )
        if latest_content_created_at == parsed_app_content_created_at:
            return Response({
                'data': "",
                'new': False,
                'error_messages': []
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'data': serializer.data,
                'new': True,
                'error_messages': []
            }, status=status.HTTP_200_OK)
