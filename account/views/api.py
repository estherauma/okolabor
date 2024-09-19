from account.serializers import (
    OTPGenerateSerializer, OTPVerifySerializer, RegistrationSerializer,
    ReportAProblemSerializer, UpdateUserPreferencesSerializer,
    UserCropExperienceSerializer, UserDocumentSerializer, UserNotificationSerializer,
    UserPreferenceSerializer, UserSerilizer, LoginSerializer,
    UserWorkexperienceSerializer
)
from account.models import (
    User, UserCropExperience, UserDocuments, UserNotification, UserPreference,
    UserReportedProblem, UserWorkExperience
)
from account.models import (
    User, UserDocuments, UserPreference, UserWorkExperience
)
from account.jwt_manager import JwtManager
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema


class RegisterView(APIView):
    @swagger_auto_schema(
        operation_summary="Register",
        tags=["Account Management"]
    )
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                email=serializer.validated_data['email'],
                curp=serializer.validated_data['curp'],
                is_active=False,
                is_verified=False
            )
            user.set_password(serializer.validated_data['password'])
            user.save()
            # user the Userserializer to return the user data
            user_serializer = UserSerilizer(user)
            return Response(
                user_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    @swagger_auto_schema(
        operation_summary="Login",
        tags=["Account Management"]
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email_or_curp = serializer.validated_data['identifier']
            try:
                user = User.objects.get(email=email_or_curp)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(curp=email_or_curp)
                except User.DoesNotExist:
                    return Response(
                        {
                            'message': (
                                'User with given information '
                                'does not exist')
                        },
                        status=status.HTTP_404_NOT_FOUND)

            if not user.is_verified or not user.is_active:
                return Response({
                    'message': 'Account not verified'},
                    status=status.HTTP_403_FORBIDDEN
                )
            if user.check_password(serializer.validated_data['password']):
                identity_manager = JwtManager()
                payload = {
                    'email': user.email,
                    'id': user.pk,
                    'firstName': user.first_name,
                    'lastName': user.last_name,
                    'isAdmin': user.is_admin,
                    'roles': (
                        list(user.groups.values_list('name', flat=True))
                        if user.groups.exists()
                        else []
                    )
                }
                token = identity_manager.encode(payload)
                return Response({
                    'token': token,
                    'data': payload
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'message': 'Invalid credentials'},
                    status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPreferencesUpdateView(APIView):
    def return_preferences(self, user, kind=None):
        if kind is not None:
            preferences = UserPreference.objects.filter(user=user, kind=kind)
        else:
            preferences = UserPreference.objects.filter(user=user)
        serializer = UserPreferenceSerializer(preferences, many=True)
        return serializer.data

    @swagger_auto_schema(
        operation_summary="Get user preferences",
        tags=["User preferences"]
    )
    def get(self, request, user_id):
        kind = request.query_params.get('kind', None)
        user = get_object_or_404(User, pk=user_id)
        preferences = self.return_preferences(user, kind)
        return Response(preferences, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create or update user preferences",
        tags=["User preferences"]
    )
    def post(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        
        # Create a new list to hold the valid preferences
        valid_preferences = []
        
        # Loop through the preferences and filter out the ones with empty or None values
        for item in request.data['preferences']:
            if item['value'] is not None and item['value'] != '':
                valid_preferences.append(item)
        
        # Replace the preferences in request.data with the valid ones
        data = {
            'preferences': valid_preferences
        }

        # Pass the filtered data to the serializer
        serializer = UpdateUserPreferencesSerializer(data=data)

        if serializer.is_valid():
            for pref_data in serializer.validated_data['preferences']:
                key = pref_data['key']
                value = pref_data['value']
                UserPreference.objects.update_or_create(
                    user=user, key=key,
                    defaults={
                        'value': value,
                        'kind': pref_data.get('kind', 'preference')
                    }
                )
            preferences = self.return_preferences(user)
            return Response(preferences, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserWorkExperienceView(APIView):
    @swagger_auto_schema(
        operation_summary="Retrieve worker experience",
        tags=["User Work Experience"]
    )
    def get(self, request, user_id):
        print(user_id)
        user = get_object_or_404(User, pk=user_id)
        experiences = UserWorkExperience.objects.filter(user=user)
        serializer = UserWorkexperienceSerializer(experiences, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create worker experiences",
        tags=["User Work Experience"]
    )
    def post(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        if len(request.data.get('end_date')) == 0:
            request.data.pop('end_date')
        serializer = UserWorkexperienceSerializer(data=request.data)
        if serializer.is_valid():
            # check if there's no entry with the same co name and startdate
            if UserWorkExperience.objects.filter(
                user=user,
                company=serializer.validated_data['company'],
                start_date=serializer.validated_data['start_date']
            ).exists():
                return Response(
                    {
                        'message': (
                                'User experience with given information '
                                'already exists'
                            )
                    },
                    status=status.HTTP_400_BAD_REQUEST)
            experience = UserWorkExperience.objects.create(
                user=user, **serializer.validated_data)
            created_experience = UserWorkexperienceSerializer(experience)
            return Response(created_experience.data, status=status.HTTP_200_OK)
        else:

            return Response(serializer.errors, status=400)

    


class UserWorkExperienceDetailsView(APIView):

    @swagger_auto_schema(
        operation_summary="Retrieve specific work experience",
        tags=["User Work Experience"]
    )
    def get(self, request, user_id, experience_id):
        experience = get_object_or_404(UserWorkExperience, pk=experience_id)
        serializer = UserWorkexperienceSerializer(experience)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Update work experience",
        tags=["User Work Experience"]
    )
    def patch(self, request, user_id, experience_id):
        experience = get_object_or_404(UserWorkExperience, pk=experience_id)
        serializer = UserWorkexperienceSerializer(
            experience, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete specific work experience",
        tags=["User Work Experience"]
    )
    def delete(self, request, user_id,  experience_id):
        experience = get_object_or_404(UserWorkExperience, pk=experience_id)
        experience.delete()
        return Response(
            {"message": "Experience deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )

class UserDocumentsView(APIView):
    @swagger_auto_schema(
        operation_summary="Retrieve user documents",
        tags=["User Documents"]
    )
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        documents = user.documents.all()
        serilizer = UserDocumentSerializer(documents, many=True)
        return Response(
            serilizer.data,
            status=status.HTTP_200_OK
        )


class UserDocumentDetailsView(APIView):
    @swagger_auto_schema(
        operation_summary="Retrieve specific document details",
        tags=["User Documents"]
    )
    def get(self, request, document_id):
        document = get_object_or_404(UserDocuments, pk=document_id)
        serilizer = UserDocumentSerializer(document)
        return Response(
            serilizer.data,
            status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        operation_summary="Delete specific document",
        tags=["User Documents"]
    )
    def delete(self, request, document_id):
        document = get_object_or_404(UserDocuments, pk=document_id)
        document.delete()
        return Response(
            {"message": "Document deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )


class ResetAccountProfile(APIView):
    @swagger_auto_schema(
        operation_summary="Reset user profile data",
        tags=["Account Management"]
    )
    def post(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        UserPreference.objects.filter(user=user).delete()
        UserDocuments.objects.filter(user=user).delete()
        UserWorkExperience.objects.filter(user=user).delete()
        return Response(
            {'message': 'Profile reset successfully'},
            status=status.HTTP_200_OK
        )


class GetOTP(APIView):
    @swagger_auto_schema(
        operation_summary="otp-generate",
        tags=["OTP"]
    )
    def post(self, request, *args, **kwargs):
        serializer = OTPGenerateSerializer(data=request.data)

        if serializer.is_valid():
            resp = serializer.start_otp_process()
            if resp == 'pending':
                user = User.objects.get(
                    id=serializer.validated_data['user_id'])
                user.telephone = serializer.validated_data['phone_number']
                user.save()
                return Response({"status": resp}, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": 'error',
                    "error": resp.get('error')
                    }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class VerifyOTP(APIView):
    @swagger_auto_schema(
        operation_summary="otp-verify",
        tags=["OTP"]
    )
    def post(self, request, *args, **kwargs):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            resp = serializer.verify_otp()
            if resp == 'approved':
                user = User.objects.get(
                    id=serializer.validated_data['user_id'])
                user.telephone_verified = True
                user.is_verified = True
                user.is_active = True
                user.save()
                # TODO: Figure out how to send localized notifications
                UserNotification.objects.create(
                    user=user,
                    title='Account Verification',
                    message='Your account has been verified successfully',
                )
                return Response({"status": resp}, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": 'error',
                    "error": resp.get('error')
                    }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class UserCropExperienceView(APIView):
    @swagger_auto_schema(
        operation_summary="Retrieve user crop experience",
        tags=["Crop Experience"]
    )
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        experiences = UserCropExperience.objects.filter(user=user)
        serializer = UserCropExperienceSerializer(experiences, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create user crop experience",
        tags=["Crop Experience"]
    )
    def post(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        experience = get_object_or_404(
            UserWorkExperience, pk=request.data.get('work_experience_id'))

        serializer = UserCropExperienceSerializer(data=request.data)

        if serializer.is_valid():
            # Check if a similar crop experience exists
            if UserCropExperience.objects.filter(
                user=user,
                crop=serializer.validated_data['crop'],
                duration=serializer.validated_data['duration'],
                duration_type=serializer.validated_data['duration_type']
            ).exists():
                return Response(
                    {
                        'message': 'Crop experience already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.validated_data.pop('work_experience')

            # Create the new UserCropExperience object
            new_experience = UserCropExperience.objects.create(
                work_experience=experience,
                user=user,
                crop=serializer.validated_data['crop'],
                kind=serializer.validated_data['kind'],
                duration=serializer.validated_data['duration'],
                duration_type=serializer.validated_data['duration_type']
            )

            # Serialize the newly created object
            created_serializer = UserCropExperienceSerializer(new_experience)

            # Return the serialized created object in the response
            return Response(
                created_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        operation_summary="Update user crop experience",
        tags=["Crop Experience"]
    )
    def patch(self, request, user_id, experience_id):
        user = get_object_or_404(User, pk=user_id)
        experience = get_object_or_404(UserWorkExperience, pk=experience_id)
        serializer = UserCropExperienceSerializer(
            experience, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserReportProblem(APIView):
    @swagger_auto_schema(
        operation_summary="Report a problem",
        tags=["Report Problem"]
    )
    def post(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        serializer = ReportAProblemSerializer(data=request.data)
        if serializer.is_valid():
            UserReportedProblem.objects.create(
                user=user, **serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserNotificationView(APIView):
    @swagger_auto_schema(
        operation_summary="Retrieve user notifications",
        tags=["User Notifications"]
    )
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        notifications = user.notifications.all()
        serializer = UserNotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create user notifications",
        tags=["User Notifications"]
    )
    def post(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        serializer = UserNotificationSerializer(data=request.data)
        if serializer.is_valid():
            UserNotification.objects.create(
                user=user, **serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Update user notifications",
        tags=["User Notifications"]
    )
    def patch(self, request, user_id):
        if not request.data.get('notification_id'):
            return Response(
                {'message': 'Notification id is required'},
                status=status.HTTP_400_BAD_REQUEST)
        notification_id = request.data.get('notification_id')
        user_id = get_object_or_404(User, pk=user_id)
        notification = get_object_or_404(UserNotification, pk=notification_id)
        serializer = UserNotificationSerializer(
            notification, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
