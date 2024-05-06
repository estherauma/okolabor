from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class ContentAPI():
    def __init__(self) -> None:
        pass

    def build_url(self):
        pass

    def get_available_languages():
        pass

    def aggregate_content():
        aggregated_content = {}

        def aggregate_form_questions():
            pass

        def aggregate_common_text():
            pass


class AggregatedContentView(APIView):
    def get(self, request):
        return Response({}, status.HTTP_200_OK)


class ContentUpdateView(APIView):
    def post(self, request):
        return Response({}, status.HTTP_200_OK)


class CompareContent(APIView):
    def get(self, request):
        return Response({}, status.HTTP_200_OK)
