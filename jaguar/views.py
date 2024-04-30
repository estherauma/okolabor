from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


class IndexView(APIView):

    def get(self, request):
        return Response({'message': 'Hello, World! Go to api/docs to see documentation'}, status.HTTP_200_OK)


schema_view = get_schema_view(
    openapi.Info(
        title="Okolabor API",
        default_version='v1',
        description="Okolabor app API Documentation",
        terms_of_service="",
        contact=openapi.Contact(email="technology@fifyteight.io"),
        license=openapi.License(name="API is licensed to 50Eight"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)
