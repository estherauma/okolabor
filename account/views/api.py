from account.serializers import RegistrationSerializer, UserSerilizer, LoginSerializer
from account.models import User

from rest_framework.exceptions import AuthenticationFailed
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
                return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid credentials'}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
