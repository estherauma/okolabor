import os
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from jaguar.serializers import UploadFileSerializer



class IndexView(APIView):
    @swagger_auto_schema(
        operation_description="This is the root of the API",
        responses={200: 'Hello, World!'},
        tags=["Root"]
    )
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


class UploadFileView(APIView):
    permission_classes = ([IsAuthenticated, ])
    upload_paths = {
        'contract': 'uploads/visa',
        'passport': 'uploads/passports',
        'profile_picture': 'uploads/profiles',
    }

    @swagger_auto_schema(
        operation_description="Upload a file",
        request_body=UploadFileSerializer,
        responses={
            201: 'File uploaded successfully',
            400: 'Bad request',
            403: 'Authenticaiton were not privided'
        },
        tags=["Files"]
    )
    def post(self, request):
        file_serializer = UploadFileSerializer(data=request.data)
        if file_serializer.is_valid():
            # based on entitytype, create upload path if not exists
            upload_path = self.upload_paths.get(request.data['entity_type'])
            if upload_path:
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)
            else:
                return Response({'error': 'Invalid entity type'}, status=status.HTTP_400_BAD_REQUEST)

            # write the file to the right path
            user_id = request.user.id
            file_path = self.upload_paths[request.data['entity_type']] + '/' + str(user_id) + '_' + file_serializer.validated_data['file_content'].name
            # get extension from file name
            file_extension = os.path.splitext(file_path)[1]
            with open(file_path, 'wb+') as destination:
                for chunk in file_serializer.validated_data['file_content'].chunks():
                    destination.write(chunk)
            return Response({
                'file_location': file_path,
                'file_type': file_extension
            }, status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
