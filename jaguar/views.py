import os
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from account.models import UserDocuments
from jaguar.serializers import UploadFileSerializer
import base64
import os
from .tasks import process_file_upload
from common.utils import StaticContent
from celery.result import AsyncResult
from django.utils.translation import gettext as _


class IndexView(APIView):
    @swagger_auto_schema(
        operation_description="This is the root of the API",
        responses={200: 'Hello, World!'},
        tags=["Root"]
    )
    def get(self, request):
        return Response({
            'message': 'Hello, World! Go to api/docs to see documentation'},
                        status.HTTP_200_OK)


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


import base64
import os
from .tasks import process_file_upload

class UploadFileView(APIView):
    permission_classes = ([IsAuthenticated, ])
    upload_paths = {
        'contract': 'uploads/visa',
        'passport': 'uploads/passports',
        'profile_picture': 'uploads/profiles',
        'english_video': 'uploads/english_videos',
        'us_driver_license': 'uploads/driver_licenses',
        'mexico_driver_license': 'uploads/driver_licenses',
        'certificate': 'uploads/certificates',
        'visa': 'uploads/visa',
        'photo': 'uploads/photos',
        'job_experience_license': 'uploads/job_experiences/licenses',
        'job_experience_media': 'uploads/job_experiences/media',
        'explanation_video': 'uploads/explanation_videos',
    }

    @swagger_auto_schema(
        operation_description="Upload a file",
        request_body=UploadFileSerializer,
        responses={
            202: 'File upload task started',
            400: 'Bad request',
            403: 'Authentication not provided'
        },
        tags=["Files"]
    )
    def post(self, request):
        serializer = UploadFileSerializer(data=request.data)
        if serializer.is_valid():
            work_experience_id = request.data.get('work_experience_id')
            entity_type = request.data['entity_type']
            upload_dir = self.upload_paths.get(entity_type)

            if not upload_dir:
                return Response({'error': 'Invalid entity type'}, status=status.HTTP_400_BAD_REQUEST)

            file = serializer.validated_data['file_content']
            file_name = f"{request.user.id}_{file.name}"
            full_path = os.path.join(upload_dir, file_name)

            # Extract file type (file extension)
            file_extension = os.path.splitext(file.name)[1]

            # Create document record in the DB before processing (to get document_id)
            document = UserDocuments.objects.create(
                user=request.user,
                path=full_path,
                kind=entity_type,
                description=request.data.get('description', ''),
                file_type=file_extension,
                work_experience_id = work_experience_id
            )

            # Encode file content to pass to Celery (base64)
            file_data_b64 = base64.b64encode(file.read()).decode()

            # Fire-and-forget task
            task = process_file_upload.delay(
                user_id=request.user.id,
                entity_type=entity_type,
                description=request.data.get('description', ''),
                file_name=file.name,
                file_path=full_path,
                file_data=file_data_b64,
                document_id=document.id  # Pass document_id to the task
            )

            return Response({
                'document_id': document.id,  # Include document_id in the response
                'task_id': task.id,
                'file_location': full_path,
                'file_type': file_extension,  # Include file_type in the response
                'status_check': f"/api/files/upload-status/{task.id}/",
                'work_experience_id': work_experience_id
            }, status=status.HTTP_202_ACCEPTED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UploadStatusView(APIView):
    permission_classes = ([IsAuthenticated, ])

    def get(self, request, task_id):
        result = AsyncResult(task_id)
        if result.state == 'PENDING':
            return Response({'status': 'Pending'}, status=200)
        elif result.state == 'SUCCESS':
            return Response({
                'status': 'Completed',
                'result': result.result
            }, status=200)
        elif result.state == 'FAILURE':
            return Response({
                'status': 'Failed',
                'error': str(result.result)
            }, status=500)
        return Response({'status': result.state}, status=200)
    
class DynamicFieldDataView(APIView):

    def get(self, request):
        content_service = StaticContent()
        field_data = {
            "Animals": {
                "field1Label": _("Animal Type"),
                "field1Options": content_service.get_animal_type_choices(),
                "field2Label": _("Tasks"),
                "field2Options": content_service.get_animal_responsibilities_choices()
            },
            "Crop and Horticulture": {
                "field1Label": _("Crop Type"),
                "field1Options": content_service.get_crop_type_choices(),
                "field2Label": _("Tasks"),
                "field2Options": content_service.get_crop_responsibilities_choices()
            },
            "Mechanics": {
                "field1Label": _("Tasks"),
                "field1Options": content_service.get_mechanics_responsibilities_choices(),
                "field2Label": None,
                "field2Options": None
            },
            "Worker Supervision/Management": {
                "field1Label": _("Tasks"),
                "field1Options": content_service.get_worker_supervision_choices(),
                "field2Label": None,
                "field2Options": None
            },
            "Licensed Vehicle Operation": {
                "field1Label": _("Tasks"),
                "field1Options": content_service.get_worker_licensed_vehicle_operation_choices(),
                "field2Label": None,
                "field2Options": None
            },
        }
        for category in field_data.values():
            for key in ['field1Options', 'field2Options']:
                if category[key]:
                    category[key] = sorted([label for _, label in category[key]])

        return Response(field_data, status=200)
