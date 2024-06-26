from account.serializers import RegistrationSerializer, UpdateUserPreferencesSerializer, UserPreferenceSerializer, UserSerilizer, LoginSerializer
from account.models import User, UserPreference
from account.jwt_manager import JwtManager
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


class RegisterView(APIView):
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

            if not user.is_verified:
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
    def return_preferences(self, user):
        preferences = UserPreference.objects.filter(user=user)
        serializer = UserPreferenceSerializer(preferences, many=True)
        return serializer.data
    
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        preferences = self.return_preferences(user)
        return Response(preferences, status=status.HTTP_200_OK)
    
    def post(self, request, user_id):
        user = get_object_or_404(User,pk=user_id)
        serializer = UpdateUserPreferencesSerializer(data=request.data)
        
        if serializer.is_valid():
            for pref_data in serializer.validated_data['preferences']:
                key = pref_data['key']
                value = pref_data['value']
                UserPreference.objects.update_or_create(
                    user=user, key=key,
                    defaults={'value': value}
                )
            preferences = self.return_preferences(user)
            return Response(preferences, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
