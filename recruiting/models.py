from django.db import models
from common.models import AuditableModel,SoftDeleteManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()




class Organization(AuditableModel):
    TYPE_CHOICES = (
        ('admin', _('addEmployerAdmin')),
        ('employer', _('addEmployerEmployer')),
        ('recruiter', _('addEmployerRecruiter')),
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=255)
    website = models.URLField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)
    description = models.TextField(help_text=_("addEmployerOrganizationDescription"))
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='recruiter')
    
    objects = SoftDeleteManager()  # Filters out deleted
    all_objects = models.Manager()

    def __str__(self):
        return f'{self.name}'


class WorkRequests(AuditableModel):
    STATUS_CHOICES = (
        ('Draft', _('createJobOrderDraft')),
        ('Requested', _('createJobOrderRequested')),
        ('Open', _('createJobOrderOpen')),
        ('Closed', _('createJobOrderClosed')),
    )
    
    name = models.CharField(max_length=255, null=False, blank=False)
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=True, blank=True)
    required_workers = models.IntegerField(null=False, blank=False)
    employer = models.ForeignKey(Organization,on_delete=models.SET_NULL,null=True,blank=True)
    status = models.CharField(
        max_length=255, null=False, blank=False,
        choices=STATUS_CHOICES, default='Open'  # Set default to 'Open'
    )
    
    objects = SoftDeleteManager()  # Only active (non-deleted)
    all_objects = models.Manager()  # All including deleted

    def __str__(self) -> str:
        return f'{self.name}'



class Role(AuditableModel):
    title = models.CharField(max_length=255)
    usdol_case_number = models.CharField(max_length=50)
    number_of_required_workers = models.IntegerField()
    description = models.TextField()
    work_type = models.CharField(null=True, blank=True, max_length=50)
    work_request = models.ForeignKey(
        WorkRequests, on_delete=models.DO_NOTHING,
        related_name='roles'
    )

    objects = SoftDeleteManager()  # Only active (non-deleted)
    all_objects = models.Manager()

    def __str__(self):
        return f'{self.title}'
    
class WorkAssignment(AuditableModel):
    STATUS_CHOICES = (
        ('assigned', 'Assigned'),
        ('offersent', 'Offer Sent'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )
    work_request = models.ForeignKey(WorkRequests, on_delete=models.CASCADE, related_name='assignments',null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="assignments",null=True, blank=True)
    worker = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='assignments',null=True, blank=True)
    assigned_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')

    def __str__(self):
        worker_name = self.worker.first_name if self.worker else 'No Worker'
        role_name = self.role.title if self.role else 'No Role'
        return f"{worker_name} - {role_name} - {self.status}"


class Hours(AuditableModel):
    role = models.OneToOneField(
        Role, on_delete=models.CASCADE,
        related_name='hours'
    )
    on_call = models.BooleanField()
    estimate_weekly_hours = models.CharField(
        max_length=50, null=True, blank=True
    )
    sunday_hours = models.CharField(max_length=50, blank=True, null=True)
    monday_hours = models.CharField(max_length=50, blank=True, null=True)
    tuesday_hours = models.CharField(max_length=50, blank=True, null=True)
    wednesday_hours = models.CharField(max_length=50, blank=True, null=True)
    thursday_hours = models.CharField(max_length=50, blank=True, null=True)
    friday_hours = models.CharField(max_length=50, blank=True, null=True)
    saturday_hours = models.CharField(max_length=50, blank=True, null=True)
    job_description = models.TextField()
    
    objects = SoftDeleteManager()  # Only active (non-deleted)
    all_objects = models.Manager()


class Wages(AuditableModel):
    role = models.OneToOneField(
        Role, on_delete=models.CASCADE, related_name='wages'
    )
    wage = models.DecimalField(max_digits=10, decimal_places=2)
    wage_type = models.CharField(
        max_length=50,
        choices=[
            ('Hourly', _('roleWagesHourly')),
            ('Daily', _('roleWagesDaily')),
            ('Weekly', _('roleWagesWeekly')),
            ('Monthly', _('roleWagesMonthly')),
        ]
    )
    piece_rate_offerings = models.DecimalField(
        max_digits=10, decimal_places=2,
        blank=True, null=True
    )
    piece_rate_offerings_type = models.CharField(
        max_length=50,
        choices=[
            ('Hourly', _('roleWagesHourly')),
            ('Daily', _('roleWagesDaily')),
            ('Weekly', _('roleWagesWeekly')),
            ('Monthly', _('roleWagesMonthly')),
        ]
    )
    frequency_of_pay = models.CharField(max_length=50)
    details = models.CharField(max_length=100, null=True)


class Deduction(AuditableModel):
    role = models.ForeignKey(
        Role, on_delete=models.CASCADE,
        related_name='deductions'
    )
    description = models.TextField()
    deduction_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()


class Qualification(AuditableModel):
    role = models.OneToOneField(
        Role, on_delete=models.CASCADE,
        related_name='qualifications'
    )
    minimum_education_requirement = models.CharField(
        max_length=50,
        
        choices=[
            ('None', _('roleQualificationNone')),
            ('Highschool/GED', _('roleQualificationHighschool/GED')),
            ('Associates', _('roleQualificationAssociates')),
            ('Bachelors', _('roleQualificationBachelors')),
            ('Masters or higher', _('roleQualificationMastersOrHigher')),
            ('Other degree', _('roleQualificationOtherDegree')),
        ]
    )
    experience_required = models.CharField(max_length=255)
    number_of_months_experience_required = models.IntegerField()
    training_required = models.CharField(max_length=255)
    number_of_months_training_required = models.IntegerField()
    certification_license_requirements = models.BooleanField()
    drug_screen = models.BooleanField()
    lifting_requirements = models.BooleanField(max_length=50)
    lifting_requirement_weight = models.IntegerField(
        blank=True, null=True
    )
    exposure_to_temperature = models.BooleanField()
    extensive_pushing_or_pulling = models.BooleanField()
    extensive_sitting_or_walking = models.BooleanField()
    frequent_stooping_or_bending_over = models.BooleanField()
    repetitive_movements = models.BooleanField()
    support_of_other_employees = models.BooleanField()
    support_of_other_employees_number = models.IntegerField(
        null=True, blank=True)
    other_qualifications = models.TextField(blank=True, null=True)


class EmploymentLocation(AuditableModel):
    role = models.OneToOneField(
        Role, on_delete=models.CASCADE,
        related_name='employment_location'
    )
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=50)
    county = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    postal_code = models.CharField(max_length=10)
    additional_info = models.TextField(blank=True, null=True)


class HousingInformation(AuditableModel):
    role = models.OneToOneField(
        Role, on_delete=models.CASCADE,
        related_name='housing_information'
    )
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=50)
    county = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    postal_code = models.CharField(max_length=10)
    type_of_housing = models.CharField(
        max_length=50,
        
        choices=[
            ('Employer provided', _('roleHousingInformationEmployerProvided')),
            ('Rental or Public', _('roleHousingInformationRentalOrPublic')),
            ]
        )
    additional_info = models.TextField(blank=True, null=True)


class MealProvision(AuditableModel):
    role = models.OneToOneField(
        Role, on_delete=models.CASCADE,
        related_name='meal_provision'
    )
    will_provide_meals = models.BooleanField()
    meal_charge_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        blank=True, null=True
    )
    additional_info = models.TextField(blank=True, null=True)


class OkoMessage(AuditableModel):
    recipient_type = models.CharField(
        max_length=50,
        choices=[
            ('Work Order', _('createMessageWorkOrder')),
            ('Email', _('createMessageEmail'))
        ]
    )
    job_order = models.ForeignKey(
        WorkRequests, on_delete=models.CASCADE,
        related_name='messages'
    )
    include_recipients = models.CharField(
        max_length=255,
        choices=[
            ('All', _('createMessageAll')),
            ('Confirmed', _('createMessageConfirmed')),
            ('Pending', _('createMessagePending')),
            ('Shortlist', _('createMessageShortlist')),
        ]
    )
    subject = models.CharField(max_length=255)
    body = models.TextField()
    auto_reply  = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.body[:50]}'


class OkoMessageRecipients(AuditableModel):
    message = models.ForeignKey(
        OkoMessage, on_delete=models.CASCADE,
        related_name='recipients'
    )
    recipient = models.ForeignKey(
        'account.User', on_delete=models.CASCADE,
        related_name='oko_messages'
    )

    def __str__(self):
        return f'{self.recipient}'
    
class EmployerRecruiter(AuditableModel):
    employer = models.ForeignKey(Organization, on_delete=models.CASCADE)
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['employer', 'recruiter'], name='unique_employer_recruiter')
        ]

    def __str__(self):
        return f"{self.recruiter.first_name} -> {self.employer.name}"


class EmployerContact(AuditableModel):
    employer = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="contacts")
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=255)
    position = models.CharField(max_length=255, blank=True, null=True) 
    is_primary = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 

    def __str__(self):
        return f'{self.name} - {self.employer.name}'
    
class EmployerRecruiterOrgLink(AuditableModel):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    employer_org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='assigned_recruiter_orgs')
    recruiter_org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='assigned_employer_orgs')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    user_updated_by = models.ForeignKey(EmployerContact, on_delete=models.SET_NULL, null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()
    class Meta:
        unique_together = ('employer_org', 'recruiter_org')
        
    def updated_by_name(self):
        if self.user_updated_by and self.user_updated_by.user:
            return f"{self.user_updated_by.user.first_name} {self.user_updated_by.user.last_name}"
        return "N/A"


    def __str__(self):
        return f"{self.employer_org.name} → {self.recruiter_org.name} [{self.status}]"
