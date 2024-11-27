import random
from account.serializers import (
    AccountRecoverSerializer, AccountResetPasswordSerializer,
    OTPGenerateSerializer,
    OTPVerifySerializer, RegistrationSerializer,
    UserDocumentSerializer, UserNotificationSerializer,
    ReportAProblemSerializer, UpdateUserPreferencesSerializer,
    UserJobExperienceDetailsSerializer,
    UserJobExperienceSerializer,
    UserPreferenceSerializer, UserSerilizer, LoginSerializer,
    UserWorkexperienceSerializer
)
from account.models import (
    User, UserJobExperience, UserDocuments, UserJobExperienceDetails,
    UserNotification, UserPreference,
    UserReportedProblem, UserWorkExperience
)
from account.jwt_manager import JwtManager
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema

from common.email import EmailHelper
from account.signals import check_passport_match_signal


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
                self.update_user_model(user, pref_data)
            preferences = self.return_preferences(user)
            return Response(preferences, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update_user_model(self, user, data):
        user_obj = User.objects.get(pk=user.id)
        if data['key'] == 'firstName':
            user_obj.first_name = data['value']
            user_obj.save()

        if data['key'] == 'lastName':
            user_obj.last_name = data['value']
            user_obj.save()

        if data['key'] == 'gender':
            user_obj.gender = data['value']
            user_obj.save()

        if data['key'] == 'dob':
            user_obj.dob = data['value']
            user_obj.save()


class UserWorkExperienceView(APIView):
    @swagger_auto_schema(
        operation_summary="Retrieve worker experience",
        tags=["User Work Experience"]
    )
    def get(self, request, user_id):
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
        if document.kind == 'passport' and document.cloud_vision_match is False:

            check_passport_match_signal.send(sender=UserDocumentDetailsView, instance=document)
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
                # update user preferences with the phone number
                phone_number = request.data.get('phone_number')
                if phone_number:
                    # Create the phone number preference
                    UserPreference.objects.update_or_create(
                        user=user, key='phone',
                        defaults={'value': phone_number, 'kind': 'preference'}
                    )
                # TODO: Figure out how to send localized notifications
                UserNotification.objects.create(
                    user=user,
                    title='Verificación de cuenta',
                    message='Su cuenta ha sido verificada exitosamente',
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


class UserJobExperienceView(APIView):
    @swagger_auto_schema(
        operation_summary="Retrieve user job experience",
        tags=["Job Experience"]
    )
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        experiences = UserJobExperience.objects.filter(user=user)
        serializer = UserJobExperienceSerializer(experiences, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create user job experience",
        tags=["Job Experience"]
    )
    def post(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        experience = get_object_or_404(
            UserWorkExperience, pk=request.data.get('work_experience_id'))

        serializer = UserJobExperienceSerializer(data=request.data)

        if serializer.is_valid():
            # Check if a similar crop experience exists
            if UserJobExperience.objects.filter(
                user=user,
                job_type=serializer.validated_data['job_type'],
                type_details=serializer.validated_data['type_details'],
                work_experience=experience
            ).exists():
                return Response(
                    {
                        'message': 'Job experience already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.validated_data.pop('work_experience')

            # Create the new UserJobExperience object
            new_experience = UserJobExperience.objects.create(
                work_experience=experience,
                user=user,
                job_type=serializer.validated_data['job_type'],
                type_details=serializer.validated_data['type_details'],
            )

            # Serialize the newly created object
            created_serializer = UserJobExperienceSerializer(new_experience)

            # Return the serialized created object in the response
            return Response(
                created_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Update user job experience",
        tags=["Job Experience"]
    )
    def patch(self, request, user_id, experience_id):
        # user = get_object_or_404(User, pk=user_id)
        experience = get_object_or_404(UserWorkExperience, pk=experience_id)
        serializer = UserJobExperienceSerializer(
            experience, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserJobExperienceDetailsView(APIView):
    @swagger_auto_schema(
        operation_summary="Add details to a job experience",
        tags=["Job Experience"]
    )
    def post(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        job_experience = get_object_or_404(
            UserJobExperience, pk=request.data.get('job_experience_id'))

        valid_data = []
        print(request.data)
        valid_data = []
        # Use parentheses with get method and provide a default empty list if 'details' is missing
        for item in request.data.get('details', []):
            if item['value'] is not None and item['value'] != '':
                valid_data.append(item)

        data = {
            'valid': valid_data,
            'created': []
        }

        # Iterate over valid data and create or update the details
        for entry in valid_data:
            exp, created = UserJobExperienceDetails.objects.update_or_create(
                job_experience=job_experience,
                created_by=user.id,
                updated_by=user.id,
                **entry
            )
            # Append serialized data of the created/updated experience detail
            data['created'].append(UserJobExperienceDetailsSerializer(exp).data)

        return Response(data, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        operation_summary='Update a user job experience detail',
        tags=["Job Experience"]
    )
    def patch(self, request, user_id):
        # user = get_object_or_404(User, pk=user_id)
        job_experience_details = get_object_or_404(
            UserJobExperienceDetails,
            pk=request.data.get('job_experience_details_id')
        )
        serilizer = UserJobExperienceDetailsSerializer(
            job_experience_details, data=request.data, partial=True)
        if serilizer.is_valid():
            serilizer.save()
            return Response(serilizer.data, status=status.HTTP_200_OK)


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


class UserAccountRecovery(APIView):
    @swagger_auto_schema(
        operation_summary="Password recovery - Request token",
        tags=["Account Management"]
    )
    def post(self, request):
        serializer = AccountRecoverSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            if user:
                reset_code = random.randrange(11111, 99999,)
                user.reset_code = reset_code
                user.save()

                email_helper = EmailHelper()
                email_helper.send_email(
                    to_emails=[user.email],
                    subject='Restablece tu contraseña de okolabor',
                    body={
                        'correo_electrónico': user.email,
                        'token_rest_contraseña': reset_code,
                    }
                )

                return Response(
                    {
                        'message': 'Please check your email for the password reset code.'
                    },
                    status.HTTP_200_OK
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAccountRecoveryReset(APIView):
    @swagger_auto_schema(
        operation_summary="Password recovery - Reset password",
        tags=["Account Management"]
    )
    def post(self, request):
        serializer = AccountResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            reset_token = serializer.validated_data['reset_token']
            password = serializer.validated_data['password']
            user = get_object_or_404(User, reset_code=reset_token)
            if user:
                user.set_password(password)
                user.reset_code = None
                user.save()

                # Send email
                email_helper = EmailHelper()
                email_helper.send_email(
                    to_emails=[user.email],
                    subject='La contraseña de tu cuenta ha cambiado.',
                    body={
                        'correo_electrónico': user.email,
                        'message': 'La contraseña de su cuenta ha cambiado. Si no inició esta solicitud, comuníquese con el soporte',
                    }
                )
                return Response(
                    {
                        'message': 'Password reset successfully.'
                    },
                    status.HTTP_200_OK
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
