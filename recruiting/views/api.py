
from drf_yasg.utils import swagger_auto_schema
from recruiting.models import Employer, Role, WorkRequests
from recruiting.serializer import (
    EmployerSerializer, RoleSerializer,
    WRRoleSerializer, WorkRequestSerializer
)
from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError


class EmployerAPIListView(ListCreateAPIView):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_summary="Retrieve list of employers",
        tags=['Employers']
    )
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create employer",
        tags=['Employers']
    )
    def post(self, requuest):
        pass


class WorkRequestsAPIListView(ListCreateAPIView):
    queryset = WorkRequests.objects.all()
    serializer_class = WorkRequestSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_summary='Retrieve all work requests',
        tags=['Work-Requests']
    )
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WorkRequestRoleDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RoleSerializer
    lookup_field = 'pk'
    queryset = Role.objects.all()

    def get_object(self):
        obj = super().get_object()
        return obj

    @swagger_auto_schema(
        operation_summary='Retrieve a specific work request role',
        tags=['Work-Requests/roles']
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Update a specific work request role',
        tags=['Work-Requests/roles']
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Partially update a specific work request role',
        tags=['Work-Requests']
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Delete a specific work request role',
        tags=['Work-Requests']
    )
    def delete(self, request, *args, **kwargs):
        pass
