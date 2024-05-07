from decouple import config
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests


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
        return documents

    def aggregate_content(self, lang_content):
        aggregated_content = {}

        def aggregate_form_questions(form_qn_data):
            question_data = []
            additional_text = []
            for item in form_qn_data['dynamic_zone']:
                if item['__component'] == 'okolabor.form-questions':
                    pass
                
                if item['__component'] == 'okolabor.additional-text':
                    pass
            return question_data, additional_text

        def aggregate_key_value_text(common_text_data):
            common_texts = []
            for item in common_text_data:
                common_texts.append({
                    'key': item['key'],
                    'value': item['value']
                })
            return common_texts
            
        def generate_select_options(z):
            pass

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
                
        
            if  item['custom_type'] == 'common_text':
                aggregation_response = aggregate_key_value_text(item['dynamic_zone'])
                page_data = {
                    'page_id': item['page_id'],
                    'page_title': item['page_title'],
                    'preview_title': item['preview_title'],
                    'data': aggregation_response
                }
                aggregated_content[item['page_id']] = page_data
    
        print(aggregated_content)
        return aggregated_content

class AggregatedContentView(APIView):
    def get(self, request):
        api = ContentAPI()
        documents = api.start_document_fetch()
        return Response(documents, status.HTTP_200_OK)


class ContentUpdateView(APIView):
    def post(self, request):
        return Response({}, status.HTTP_200_OK)


class CompareContent(APIView):
    def get(self, request):
        return Response({}, status.HTTP_200_OK)
