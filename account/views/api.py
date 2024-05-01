from account.serializers import RegistrationSerializer, UserSerilizer
from account.models import User


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
