from django.db import models
from common.models import AuditableModel


class Employer(AuditableModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=255)
    website = models.URLField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name}'


class WorkRequests(AuditableModel):
    STATUS_CHOICES = (
        ('Draft', 'Draft'),
        ('Requested', 'Requested'),
        ('Open', 'Open'),
        ('Closed', 'Closed'),
    )
    name = models.CharField(max_length=255, null=False, blank=False)
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=True, blank=True)
    required_workers = models.IntegerField(null=False, blank=False)
    employer = models.ForeignKey(Employer, on_delete=models.DO_NOTHING)
    status = models.CharField(
        max_length=255, null=False, blank=False,
        choices=STATUS_CHOICES, default='DRAFT'
    )

    def __str__(self) -> str:
        return f'{self.name}'


class Role(AuditableModel):
    title = models.CharField(max_length=255)
    usdol_case_number = models.CharField(max_length=50)
    number_of_required_workers = models.IntegerField()
    description = models.TextField(default='No description provided')
    work_request = models.ForeignKey(
        WorkRequests, on_delete=models.DO_NOTHING,
        related_name='roles'
    )

    def __str__(self):
        return f'{self.title}'


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


class Wages(AuditableModel):
    role = models.OneToOneField(
        Role, on_delete=models.CASCADE, related_name='wages'
    )
    wage = models.DecimalField(max_digits=10, decimal_places=2)
    wage_type = models.CharField(
        max_length=50,
        choices=[
            ('Hourly', 'Hourly'),
            ('Daily', 'Daily'),
            ('Weekly', 'Weekly'),
            ('Monthly', 'Monthly')
        ]
    )
    piece_rate_offerings = models.DecimalField(
        max_digits=10, decimal_places=2,
        blank=True, null=True
    )
    piece_rate_offerings_type = models.CharField(
        max_length=50,
        choices=[
            ('Hourly', 'Hourly'),
            ('Daily', 'Daily'),
            ('Weekly', 'Weekly'),
            ('Monthly', 'Monthly')
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


class Qualification(AuditableModel):
    role = models.OneToOneField(
        Role, on_delete=models.CASCADE,
        related_name='qualifications'
    )
    minimum_education_requirement = models.CharField(
        max_length=50,
        choices=[
            ('None', 'None'),
            ('Highschool/GED', 'Highschool/GED'),
            ('Associates', 'Associates'),
            ('Bachelors', 'Bachelors'),
            ('Masters or higher', 'Masters or higher'),
            ('Other degree', 'Other degree')
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
            ('Employer provided', 'Employer provided'),
            ('Rental or Public', 'Rental or Public')
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
