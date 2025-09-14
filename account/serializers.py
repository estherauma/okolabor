from rest_framework import serializers
from account.models import (
    User, UserJobExperience, UserDocuments, UserJobExperienceDetails,
    UserNotification, UserPreference,
    UserWorkExperience,LanguageChoices
)
import re
from common.twilio import OTPVerification
from django.core.exceptions import ObjectDoesNotExist
from common.logger import AppLogger

logger = AppLogger(log_file='logs/invalid-curps.log')


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
            logger.info(f'CURP can not be more than 18 characters long: {value}')
            raise serializers.ValidationError(
                'CURP cannot be more than 18 characters long')
        if len(value) < 18:
            logger.info(f'CURP cannot be less than 18 characters long: {value}')
            raise serializers.ValidationError(
                'CURP cannot be less than 18 characters long')
        if not re.match(r'^[A-Za-z]{4}\d{6}[A-Za-z]{6}[A-Za-z0-9]{1}\d{1}$', value):
            logger.info(f'Invalid CURP format: {value}')
            raise serializers.ValidationError('Invalid CURP format')

        # Commenting this out just incase they come back and ask that we put it back.
        # if User.objects.filter(curp=value).exists():
        #     logger.info(f'User with the given CURP already exists: {value}')
        #     raise serializers.ValidationError(
        #         'User with given CURP already exists')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError({
                'error_key': 'email_exists',
                'message': 'Email already exists'
            })
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


class BlankableDateField(serializers.DateField):
    def to_internal_value(self, data):
        if data in ("", None):
            return None
        return super().to_internal_value(data)

class BlankableBooleanField(serializers.BooleanField):
    def to_internal_value(self, data):
        if data in ("", None, ""):
            return None
        return super().to_internal_value(data)


class UserWorkexperienceSerializer(serializers.ModelSerializer):
    country = serializers.CharField(required=False, allow_blank=True)
    state = serializers.CharField(required=False, allow_blank=True)
    visa_type = serializers.CharField(required=False, allow_blank=True)
    company = serializers.CharField(required=True)
    start_date = BlankableDateField(required=False, allow_null=True)
    currently_working = BlankableBooleanField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    work_title = serializers.CharField(required=True)
    supervisor_name = serializers.CharField(required=False, allow_blank=True)
    supervisor_tel = serializers.CharField(required=False, allow_blank=True)
    supervisor_email = serializers.CharField(required=False, allow_blank=True)
    work_under_h2a_in_usa = serializers.CharField(allow_blank=True, required=False)
    type_of_work = serializers.CharField(required=True)
    approx_month_and_year = serializers.CharField(
        required=False, allow_blank=True, default='Not specified'
    )
    approx_total_months_worked = serializers.CharField(
        required=False, allow_blank=True, default='Not specified'
    )
    
    def validate_start_date(self, value):
        print(f"Validating start_date: {value}")
        # Convert "" → None
        if value in ["", None]:
            return None
        return value

    class Meta:
        model = UserWorkExperience
        fields = [
            'id', 'country', 'state', 'visa_type','company', 'start_date',
            'currently_working','end_date', 'work_title',
            'supervisor_name', 'supervisor_tel', 'supervisor_email',
            'work_under_h2a_in_usa','type_of_work', 'approx_month_and_year',
            'approx_total_months_worked'
        ]


class UserDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDocuments
        exclude = ['cloud_vision_response']


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
            user_id = self.validated_data.get('user_id')

            # Default locale
            locale = 'es'

            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    user_language = user.language if user.language else locale
                    # Normalize 'es-MX' to 'es'
                    if user_language.lower() == 'es-mx':
                        locale = 'es'
                    else:
                        locale = user_language
                except ObjectDoesNotExist:
                    # User not found, fallback to default locale
                    pass

            otp_service = OTPVerification()
            response = otp_service.send_otp(phone_number, locale=locale)
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





class ReportAProblemSerializer(serializers.Serializer):
    is_anonymous = serializers.BooleanField()
    report_recipient = serializers.EmailField()
    description = serializers.CharField()


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
