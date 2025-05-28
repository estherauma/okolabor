from rest_framework import serializers
from account.models import (
    User, UserJobExperience, UserDocuments, UserJobExperienceDetails, UserNotification, UserPreference,
    UserReportedProblem, UserWorkExperience,LanguageChoices
)
import re
from common.twilio import OTPVerification


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    curp = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    password_repeat = serializers.CharField(required=True)
    language = serializers.CharField(required=False)
    
    
    def validate_language(self, value):
        if value in [None, '']:
            return value 
        if value not in [LanguageChoices.EN, LanguageChoices.ES_MX]:
            raise serializers.ValidationError(
                'Language must be either "en" or "es-MX".'
            )
        return value


    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                'Password must be at least 8 characters long')
        if value != self.initial_data.get('password_repeat'):
            raise serializers.ValidationError('Passwords do not match')
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                'Password must contain at least one number')
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError(
                'Password must contain at least one uppercase letter')
        return value

    def validate_curp(self, value):
        if len(value) > 18:
            raise serializers.ValidationError(
                'CURP cannot be more than 18 characters long')
        if len(value) < 18:
            raise serializers.ValidationError(
                'CURP cannot be less than 18 characters long')
        if not re.match(r'^[A-Za-z]{4}\d{6}[A-Za-z]{6}\d{2}$', value):
            raise serializers.ValidationError('Invalid CURP format')
        if User.objects.filter(curp=value).exists():
            raise serializers.ValidationError(
                'User with given CURP already exists')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value


class UserSerilizer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'curp', 'is_active', 'is_verified','language')


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate_identifier(self, value):
        if (
            not User.objects.filter(email=value).exists()
            and not User.objects.filter(curp=value).exists()
        ):
            raise serializers.ValidationError(
                'User with given information does not exist')
        return value


class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = ['key', 'value', 'kind']


class UpdateUserPreferencesSerializer(serializers.Serializer):
    preferences = UserPreferenceSerializer(many=True)


class UserWorkexperienceSerializer(serializers.ModelSerializer):
    country = serializers.CharField(required=False, allow_blank=True)
    state = serializers.CharField(required=False, allow_blank=True)
    visa_type = serializers.CharField(required=False, allow_blank=True)
    company = serializers.CharField(required=True)
    start_date = serializers.DateField(required=True)
    currently_working = serializers.BooleanField(required=False)    
    end_date = serializers.DateField(required=False, allow_null=True)
    work_title = serializers.CharField(required=True)
    supervisor_name = serializers.CharField(required=False, allow_blank=True)
    supervisor_tel = serializers.CharField(required=False, allow_blank=True)
    supervisor_email = serializers.EmailField(required=False, allow_blank=True)
    work_under_h2a_in_usa = serializers.CharField(allow_blank=True, required=False)
    

    class Meta:
        model = UserWorkExperience
        fields = [
            'id', 'country', 'state', 'visa_type','company', 'start_date',
            'currently_working','end_date', 'work_title',
            'supervisor_name', 'supervisor_tel', 'supervisor_email','work_under_h2a_in_usa'
        ]


class UserDocumentSerializer(serializers.ModelSerializer):
    work_experience_id = serializers.SerializerMethodField()

    class Meta:
        model = UserDocuments
        exclude = ['cloud_vision_response']

    def get_work_experience_id(self, obj):
        doc_to_experience = self.context.get('doc_to_experience', {})
        return doc_to_experience.get(obj.id)


class OTPGenerateSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15, required=True)
    user_id = serializers.CharField(max_length=36)
    regenerate = serializers.BooleanField(required=False, default=False)

    def validate_phone_number(self, value):
        
        if not value.startswith('+'):
            raise serializers.ValidationError(
                "Phone number must start with a '+' sign and include the country code.")
        if not value[1:].isdigit():
            raise serializers.ValidationError(
                "Phone number must contain only digits after the country code."
            )
        if self.initial_data.get('regenerate'):
            return value
        # make sure the phone number is unique
        if User.objects.filter(telephone=value).exists():
            raise serializers.ValidationError(
                "Phone number already exists"
            )
        return value

    def start_otp_process(self):
        try:
            phone_number = self.validated_data['phone_number']
            otp_service = OTPVerification()
            response = otp_service.send_otp(phone_number)
            return response
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}


class OTPVerifySerializer(serializers.Serializer):
    otp_code = serializers.CharField(max_length=15, required=True)
    phone_number = serializers.CharField(max_length=15, required=True)
    user_id = serializers.CharField(max_length=36)

    def validate_phone_number(self, value):
        if not value.startswith('+'):
            raise serializers.ValidationError(
                "Phone number must start with a '+'"
                "sign and include the country code."
            )
        if not value[1:].isdigit():
            raise serializers.ValidationError(
                "Phone number must contain only "
                "digits after the country code."
            )
        return value

    def validate_otp_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(
                'OTP must be a number'
            )

        if len(value) < 4:
            raise serializers.ValidationError(
                'OTP must be 4 characters long'
            )
        return value

    def verify_otp(self):
        try:
            phone_number = self.validated_data['phone_number']
            otp_code = self.validated_data['otp_code']
            otp_service = OTPVerification()
            response = otp_service.check_otp(otp_code, phone_number)
            return response
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}


class UserJobExperienceDetailsSerializer(serializers.ModelSerializer):
    # job_experience = UserJobExperienceSerializer(read_only=True)
    job_experience_id = serializers.PrimaryKeyRelatedField(
        queryset=UserJobExperience.objects.all(), write_only=True, 
        source='job_experience'
    )
    class Meta:
        model = UserJobExperienceDetails
        fields = [ 'id','kind', 'value', 'is_attachment','job_experience_id']


class UserJobExperienceSerializer(serializers.ModelSerializer):
    # Nest the related work experience
    work_experience = UserWorkexperienceSerializer(read_only=True)  # For GET requests
    work_experience_id = serializers.PrimaryKeyRelatedField(
        queryset=UserWorkExperience.objects.all(), write_only=True, source='work_experience'
    )  # For POST requests
    
    # Include job_experience_details in the serializer as a nested field
    job_experience_details = UserJobExperienceDetailsSerializer(many=True, read_only=True)

    class Meta:
        model = UserJobExperience
        fields = [
            'id', 'job_type', 'type_details',
            'work_experience', 'work_experience_id',
            'job_experience_details'
        ]





class ReportAProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReportedProblem
        fields = ['topic', 'description']
        read_only_fields = ['id', 'user_id']


class UserNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotification
        fields = ['id', 'title', 'message','status', 'category']
        read_only_fields = [ 'id', 'user_id', 'read_at']


class AccountRecoverSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('User with given email does not exist')
        return value


class AccountResetPasswordSerializer(serializers.Serializer):
    reset_token = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    password_repeat = serializers.CharField(required=True)

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                'Password must be at least 8 characters long')
        if value != self.initial_data.get('password_repeat'):
            raise serializers.ValidationError('Passwords do not match')
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                'Password must contain at least one number')
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError(
                'Password must contain at least one uppercase letter')
        return value
