from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import AuditableModel, BaseModel


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """

        if not email:
            raise ValueError('Email field must be set')

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class LanguageChoices(models.TextChoices):
    EN = 'en', 'English'
    ES_MX = 'es-MX', 'Español (Mexico)'

class User(AbstractBaseUser, AuditableModel, PermissionsMixin):
    email = models.EmailField('email address', unique=True)
    curp = models.CharField('curp', max_length=18, unique=True)
    first_name = models.CharField('first name', max_length=30, blank=True)
    last_name = models.CharField('last name', max_length=30, blank=True)
    middle_name = models.CharField('middle name', max_length=30, blank=True)
    is_active = models.BooleanField('active', default=True)
    is_verified = models.BooleanField('verified', default=False)
    is_staff = models.BooleanField(default=False)
    reset_password_token = models.CharField(null=True,
                                            blank=True, max_length=125)
    profile_image = models.URLField(null=True, blank=True)
    language = models.CharField(max_length=10, default=LanguageChoices.ES_MX,
                                choices=LanguageChoices.choices)
    access_code = models.CharField('access_code', null=True,
                                   blank=True, max_length=30)
    position = models.CharField('position', null=True,
                                blank=True, max_length=30)
    telephone = models.CharField('telephone', unique=False,
                                 null=True, blank=True, max_length=30)
    telephone_verified = models.BooleanField('telephone_verified',
                                             default=False)
    mobile = models.CharField('mobile', null=True, blank=True,
                              max_length=30)
    address_line_1 = models.CharField('address_line_1',
                                      null=True, blank=True, max_length=30)
    address_line_2 = models.CharField('address_line_2',
                                      null=True, blank=True, max_length=30)
    address_line_3 = models.CharField('address_line_3',
                                      null=True, blank=True, max_length=30)
    city = models.CharField('city', null=True, blank=True, max_length=30)
    passport_number = models.CharField('passport_number',
                                       null=True, blank=True, max_length=30)
    gender = models.CharField(max_length=15,  blank=True, null=True)
    dob = models.DateField(null=True, blank=True)
    reset_code = models.CharField(max_length=256, null=True, blank=True)

    USERNAME_FIELD = 'curp'

    objects = UserManager()

    @property
    def is_admin(self):
        return self.is_superuser

    def __str__(self):
        return f'{self.email} {self.last_name}'
    
    def get_full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}".strip()


class LoginEvent(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='login_events')
    ip_address = models.GenericIPAddressField()
    date_logged_in = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'login_events'

    def __str__(self) -> str:
        return f('{self.user.email}@{self.ip_address} logged in at {self.date_logged_in}')


class UserPreference(AuditableModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=256, null=False, blank=False)
    value = models.CharField(max_length=256, null=False, blank=False)
    kind = models.CharField(
        max_length=256, null=False, default='preference', blank=False)

    def __str__(self):
        return f'{self.user.curp} - {self.key}'

    class Meta:
        db_table = 'account_user_preferences'


class UserWorkExperience(AuditableModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='work_experiences')
    country = models.CharField(max_length=256, null=True, blank=True)
    state = models.CharField(max_length=256, null=True, blank=True)
    visa_type = models.CharField(max_length=256, null=True, blank=True)
    company = models.CharField(max_length=256, null=False, blank=False)
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=True, blank=True)
    work_title = models.CharField(max_length=256, null=True, blank=True)
    supervisor_name = models.CharField(max_length=256, null=True, blank=True)
    supervisor_tel = models.CharField(max_length=256, null=True, blank=True)
    supervisor_email = models.EmailField(null=True, blank=True)
    work_under_h2a_in_usa = models.CharField(
        blank=True, null=True, max_length=256, default='No')

    def __str__(self):
        return f'{self.user.curp} - {self.company}'

    class Meta:
        db_table = 'account_user_work_experience'


class UserWorkExperienceDocuments(AuditableModel):
    work_experience = models.ForeignKey(
        UserWorkExperience,
        on_delete=models.CASCADE, related_name='documents')
    document = models.FileField(upload_to='documents/')
    kind = models.CharField(max_length=256, null=False, blank=False)

    def __str__(self):
        return f'{self.work_experience.user.curp} - {self.kind}'

    class Meta:
        db_table = 'account_user_work_experience_documents'


class UserDocuments(AuditableModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='documents')
    path = models.CharField(max_length=256, null=True, blank=True)
    kind = models.CharField(max_length=256, null=True, blank=True)
    description = models.TextField()
    cloud_vision_response = models.TextField(null=True, blank=True)
    cloud_vision_match = models.BooleanField(default=False)
    file_type = models.CharField(max_length=256, null=True, blank=True)


class UserJobExperience(AuditableModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='crop_experiences')
    work_experience = models.ForeignKey(
        UserWorkExperience, on_delete=models.CASCADE,
        related_name='crop_experiences', null=True, blank=True)
    job_type = models.CharField(max_length=256, null=False, blank=False)
    type_details = models.CharField(max_length=256, null=True, blank=True)
    # duration = models.IntegerField(null=False, blank=False)
    # duration_type = models.CharField(max_length=256, null=False, blank=False)


    def __str__(self):
        return f'{self.user.curp} - {self.job_type}'

class UserJobExperienceDetails(AuditableModel):
    KIND_CHOICES = (
        ('responsibilities', 'Responsibilities'),
        ('explanation', 'Explanation'),
        ('license', 'License'),
        ('evidence', 'Evidence'),
        ('visa', 'Visa'),
        ('explanation_video', 'Explanation Video'),
    )
    job_experience = models.ForeignKey(
        UserJobExperience, on_delete=models.CASCADE,
        related_name='job_experience_details')
    kind = models.CharField(max_length=256, null=False, blank=False)
    value = models.CharField(max_length=256, null=False, blank=False)
    is_attachment = models.BooleanField(default=False)


    def __str__(self):
        return f'{self.job_experience.work_experience.company}'

    class Meta:
        db_table = 'account_user_crop_experience_details'


class UserReportedProblem(AuditableModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reported_problems')
    topic = models.CharField(max_length=256, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    solution = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=256, default='pending')
    resolved_by = models.ForeignKey(
            User, on_delete=models.CASCADE, related_name='resolved_problems',
            null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.curp} - {self.topic} - {self.status}'


class UserNotification(AuditableModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=256, null=False, blank=False)
    category = models.CharField(
        max_length=256, null=False, blank=False, default='general')
    message = models.TextField(null=False, blank=False)
    status = models.CharField(max_length=256, default='unread')
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.curp} - {self.title} - {self.status}'


class UserActivityLog(AuditableModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=256, null=False, blank=False)
    details = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.curp} - {self.action} - {self.created_at}'
