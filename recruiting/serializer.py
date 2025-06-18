from rest_framework import serializers

from recruiting.models import (
    Deduction, Organization, EmploymentLocation, Hours, HousingInformation,
    MealProvision, Qualification, Role, Wages, WorkRequests
)


class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


class EmploymentLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmploymentLocation
        fields = '__all__'


class WRRoleSerializer(serializers.ModelSerializer):
    employment_location = EmploymentLocationSerializer()

    class Meta:
        model = Role
        fields = '__all__'


class WorkRequestSerializer(serializers.ModelSerializer):
    roles = WRRoleSerializer(many=True, read_only=True)
    employer = EmployerSerializer(read_only=True)

    class Meta:
        model = WorkRequests
        fields = '__all__'
        
class RoleWorkRequestSerializer(serializers.ModelSerializer):
    employer = EmployerSerializer(read_only=True)

    class Meta:
        model = WorkRequests
        fields = '__all__'


class HoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hours
        fields = '__all__'


class WageSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = Wages
        fields = '__all__'


class DeductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deduction
        fields = '__all__'


class QualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qualification
        fields = '__all__'


class HousingInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HousingInformation
        fields = '__all__'


class MealProvisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealProvision
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    hours = HoursSerializer(read_only=True)
    wages = WageSerilaizer(read_only=True)
    deductions = DeductionSerializer(many=True, read_only=True)
    qualifications = QualificationSerializer(read_only=True)
    employment_location = EmploymentLocationSerializer(read_only=True)
    housing_information = HousingInformationSerializer(read_only=True)
    meal_provision = MealProvisionSerializer(read_only=True)
    work_request = RoleWorkRequestSerializer(read_only=True)
    accept_status = serializers.SerializerMethodField()  # 👈 Add this line

    class Meta:
        model = Role
        fields = '__all__'  # This will now include `accept_status`

    def get_accept_status(self, obj):
        user = self.context['request'].user
        qs = obj.assignments.filter(worker=user)

        if qs.filter(status='confirmed').exists():
            return 'accepted'
        if qs.filter(status='rejected').exists():
            return 'rejected'
        if qs.filter(status='offersent').exists():
            return 'offersent'
        if qs.filter(status='cancelled').exists():
            return 'cancelled'
        return None

class OrganizationSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['name', 'type', 'email']

class EmployerRecruiterPairSerializer(serializers.Serializer):
    employer = OrganizationSummarySerializer()
    recruiter = OrganizationSummarySerializer()