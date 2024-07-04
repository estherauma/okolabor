from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from common.models import AuditableModel
from django.utils.translation import gettext_lazy as _
from common.models import BaseModel


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


class User(AbstractBaseUser, AuditableModel, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    curp = models.CharField(_('curp'), max_length=18, unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    middle_name = models.CharField(_('middle name'), max_length=30, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_verified = models.BooleanField(_('verified'), default=False)
    is_staff = models.BooleanField(default=False)
    reset_password_token = models.CharField(null=True, blank=True, max_length=125)
    profile_image = models.URLField(null=True, blank=True)
    access_code = models.CharField(_('access_code'), null=True, blank=True, max_length=30)
    position = models.CharField(_('position'), null=True, blank=True, max_length=30)
    telephone = models.CharField(_('telephone'), null=True, blank=True, max_length=30)
    mobile = models.CharField(_('mobile'), null=True, blank=True, max_length=30)
    address_line_1 = models.CharField(_('address_line_1'), null=True, blank=True, max_length=30)
    address_line_2 = models.CharField(_('address_line_2'), null=True, blank=True, max_length=30)
    address_line_3 = models.CharField(_('address_line_3'), null=True, blank=True, max_length=30)
    city = models.CharField(_('city'), null=True, blank=True, max_length=30)
    passport_number = models.CharField(_('passport_number'), null=True, blank=True, max_length=30)
    gender = models.CharField(max_length=15,  blank=True, null=True)
    dob = models.DateField(null=True, blank=True)

    USERNAME_FIELD = 'curp'

    objects = UserManager()

    @property
    def is_admin(self):
        return self.is_superuser

    def __str__(self):
        return f'{self.email} {self.last_name}'


class LoginEvent(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='login_events')
    ip_address = models.GenericIPAddressField()
    date_logged_in = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'login_events'

    def __str__(self) -> str:
        return f'{self.user.email}@{self.ip_address} logged in at {self.date_logged_in}'

class UserPreference(AuditableModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=256, null=False, blank=False)
    value = models.CharField(max_length=256, null=False, blank=False)
    kind = models.CharField(max_length=256, null=False, default='preference', blank=False)

    def __str__(self):
        return f'{self.user.curp} - {self.key}'

    class Meta:
        db_table = 'account_user_preferences'
