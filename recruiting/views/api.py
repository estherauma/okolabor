
from drf_yasg.utils import swagger_auto_schema
from recruiting.models import Organization, Role, WorkRequests, WorkAssignment,EmployerRecruiterOrgLink,RecruiterOrganizationEmployer
from recruiting.serializer import (
    EmployerSerializer, RoleSerializer,
    WRRoleSerializer, WorkRequestSerializer,OrganizationSummarySerializer,EmployerRecruiterPairSerializer
)
from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView,ListAPIView
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


class RoleAPIListView(ListAPIView):
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return roles with assignments confirmed or rejected for the current user
        return Role.objects.filter(
            assignments__worker=self.request.user,
            assignments__status__in=['confirmed', 'rejected','offersent','cancelled']
        ).distinct()

    @swagger_auto_schema(
        operation_summary='Retrieve roles accepted or declined by the user, including accept status.',
        tags=['Roles']
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
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
        
class WorkerConfirmedOrganizationsAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployerRecruiterPairSerializer

    @swagger_auto_schema(
        operation_summary='List confirmed employer–recruiter pairs for the authenticated worker',
        tags=['Worker - Confirmed Employer-Recruiter Pairs']
    )
    def get(self, request, *args, **kwargs):
        worker = request.user

        # Fetch confirmed assignments
        confirmed_assignments = WorkAssignment.objects.filter(
            worker=worker,
            status='confirmed',
            work_request__isnull=False
        ).select_related('work_request__employer')

        seen_pairs = set()
        result = []

        for assignment in confirmed_assignments:
            employer = assignment.work_request.employer
            if not employer:
                continue

            # Get recruiters linked to this employer
            recruiter_links = RecruiterOrganizationEmployer.objects.filter(
                employer_organization=employer
            ).select_related('recruiter_organization')

            for link in recruiter_links:
                recruiter = link.recruiter_organization
                pair_key = (employer.id, recruiter.id)

                if pair_key not in seen_pairs:
                    seen_pairs.add(pair_key)
                    result.append({
                        'employer': employer,
                        'recruiter': recruiter
                    })

        serializer = self.get_serializer(result, many=True)
        return Response(serializer.data)