

from recruiting.models import Employer
from recruiting.serializer import EmployerSerializer
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class EmployerAPIListView(ListCreateAPIView):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
       serializer = self.get_serializer(self.get_queryset(), many=True)
       return Response(serializer.data, status=status.HTTP_200_OK)
