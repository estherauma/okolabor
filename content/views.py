from decouple import config
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import asyncio


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
        # save aggregated content to database
        self.documents = documents
        print(documents)
        return documents
           


    def aggregate_content(self, lang_content):
        print('aggregating')
        aggregated_content = {}

        def aggregate_form_questions(form_qn_data):
            question_data = []
            additional_text = []
            pass

        def aggregate_common_text():
            pass
        for item in lang_content['data']:
            if item['custom_type'] == 'form_questions':
                aggregate_form_questions(item)
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
