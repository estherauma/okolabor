from rest_framework import serializers

from recruiting.models import (
    Deduction, Employer, EmploymentLocation, Hours, HousingInformation,
    MealProvision, Qualification, Role, Wages, WorkRequests
)


class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
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

    class Meta:
        model = Role
        fields = '__all__'
