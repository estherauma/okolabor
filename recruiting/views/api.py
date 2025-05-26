
from drf_yasg.utils import swagger_auto_schema
from recruiting.models import Organization, Role, WorkRequests, WorkAssignment
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
from rest_framework.views import APIView


class EmployerAPIListView(ListCreateAPIView):
    queryset = Organization.objects.all()
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
        operation_summary='Retrieve all Job Orders',
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
        tags=['Work-Requests']
    )
    def get(self, request, *args, **kwargs): 
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Update a specific work request role',
        tags=['Work-Requests']
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


class RoleAPIListView(ListCreateAPIView):
    serializer_class = RoleSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        
        return Role.objects.filter(
            assignments__worker=self.request.user,
            assignments__status='offersent'
        ).distinct()
    

    @swagger_auto_schema(
        operation_summary='Retrieve roles with offers sent to the user',
        tags=['Roles']
    )
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AcceptRoleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Accept a role offer",
        tags=["Roles"]
    )
    def post(self, request, role_id):
        user = request.user

        try:
            assignment = WorkAssignment.objects.get(
                role_id=role_id,
                worker=user,
                status='offersent'
            )
            assignment.status = 'confirmed'
            assignment.save()
            return Response({"detail": "Role offer accepted."}, status=status.HTTP_200_OK)

        except WorkAssignment.DoesNotExist:
            print("No assignment found for role_id with status 'offersent' and user.")
            return Response({"detail": "Offer not found or already processed."}, status=status.HTTP_404_NOT_FOUND)

class RejectRoleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Reject a role offer",
        tags=["Roles"]
    )
    def post(self, request, role_id):
        try:
            assignment = WorkAssignment.objects.get(
                role_id=role_id,
                worker=request.user,
                status='offersent'
            )
            assignment.status = 'rejected'
            assignment.save()
            return Response({"detail": "Role offer rejected."}, status=status.HTTP_200_OK)
        except WorkAssignment.DoesNotExist:
            return Response({"detail": "Offer not found or already processed."}, status=status.HTTP_404_NOT_FOUND)