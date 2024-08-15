from account.serializers import RegistrationSerializer, UpdateUserPreferencesSerializer, UserPreferenceSerializer, UserSerilizer, LoginSerializer, UserWorkexperienceSerializer
from account.models import User, UserPreference, UserWorkExperience
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
            return Response(user_serializer.data, status=status.HTTP_201_CREATED)
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
                    return Response({'message': 'User with given information does not exist'}, status=status.HTTP_404_NOT_FOUND)

            if not user.is_verified or not user.is_active:
                return Response({'message': 'Account not verified'}, status=status.HTTP_403_FORBIDDEN)
            if user.check_password(serializer.validated_data['password']):
                identity_manager = JwtManager()
                payload = {
                    'email': user.email,
                    'id': user.pk,
                    'firstName': user.first_name,
                    'lastName': user.last_name,
                    'isAdmin': user.is_admin,
                    'roles': list(user.groups.values_list('name', flat=True)) if user.groups.exists() else [],
                }
                token = identity_manager.encode(payload)
                return Response({
                    'token': token,
                    'data': payload
                }, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid credentials'}, status=status.HTTP_403_FORBIDDEN)
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
        serializer = UpdateUserPreferencesSerializer(data=request.data)

        if serializer.is_valid():
            for pref_data in serializer.validated_data['preferences']:
                key = pref_data['key']
                value = pref_data['value']
                UserPreference.objects.update_or_create(
                    user=user, key=key,
                    defaults={'value': value, 'kind': pref_data.get('kind', 'preference')}
                )
            preferences = self.return_preferences(user)
            return Response(preferences, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserWorkExperienceView(APIView):
    @swagger_auto_schema(
        operation_summary="Retrieve worker experience",
        tags=["User Experience"]
    )
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        experiences = UserWorkExperience.objects.filter(user=user)
        serializer = UserWorkexperienceSerializer(experiences, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create worker experiences",
        tags=["User Experience"]
    )
    def post(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        serializer = UserWorkexperienceSerializer(data=request.data)
        if serializer.is_valid():
            # check if there's no entry with the same company name and start date
            if UserWorkExperience.objects.filter(
                user=user,
                company=serializer.validated_data['company'],
                start_date=serializer.validated_data['start_date']
            ).exists():
                return Response({'message': 'Work experience with same company name and start date already exists'},
                                status=status.HTTP_400_BAD_REQUEST)
            UserWorkExperience.objects.create(user=user, **serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:

            return Response(serializer.errors, status=400)

    @swagger_auto_schema(
        operation_summary="Update user experience",
        tags=["User Experience"]
    )
    def patch(self, request, user_id, experience_id):
        user = get_object_or_404(User, pk=user_id)
        experience = get_object_or_404(UserWorkExperience, pk=experience_id)
        serializer = UserWorkexperienceSerializer(experience, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
