from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from account.models import User, UserJobExperience, UserJobExperienceDetails, UserWorkExperience
from decouple import config

# faker
from faker import Faker
from recruiting.models import (
    Deduction, EmploymentLocation, Hours, HousingInformation,
    MealProvision, Organization, Qualification, Role, Wages, WorkRequests
)
import random
fake = Faker()


class Command(BaseCommand):
    help = 'Create test data'

    def handle(self, *args, **options):
        print('Creating organizations')
        self.create_organizations()
        self.create_work_experiences()
      
    def create_organizations(self):
        def generate_email(company_name):
            username = fake.user_name().replace('.', '').replace('-', '')
            domain = "okolabor.com"
            return f"{username}@{domain}"

        def create_employers():
            for _ in range(25):
                company_name = fake.company()
                Organization.objects.create(
                    name=company_name,
                    email=generate_email(company_name),
                    phone=fake.phone_number(),
                    website=fake.url(),
                    address=fake.street_address(),
                    city=fake.city(),
                    state=fake.state(),
                    country=fake.country(),
                    zip_code=fake.zipcode(),
                    description=fake.sentence(words=3),
                    is_active=True,
                    is_verified=random.choice([True, False]),
                    type='employer'
                )

        def create_recruiters():
            for _ in range(25):
                company_name = fake.company()
                Organization.objects.create(
                    name=company_name,
                    email=generate_email(company_name),
                    phone=fake.phone_number(),
                    website=fake.url(),
                    address=fake.street_address(),
                    city=fake.city(),
                    state=fake.state(),
                    country=fake.country(),
                    zip_code=fake.zipcode(),
                    description=fake.sentence(words=3),
                    is_active=True,
                    is_verified=random.choice([True, False]),
                    type='recruiter'
                )
            # Start to create Job Orders
            self.create_job_orders()
        create_employers()
        create_recruiters()
    
    def create_job_orders(self):
        print('Test organizations created successfully')
        print('Proceeding to create job orders')
        
        def create_hours(role):
            def random_hours():
                start = random.randint(6, 10)
                end = start + random.choice([4, 6, 8])
                return f"{start}:00 - {end}:00"

            work_days = {
                'sunday_hours': random.choice([random_hours(), None]),
                'monday_hours': random_hours(),
                'tuesday_hours': random_hours(),
                'wednesday_hours': random_hours(),
                'thursday_hours': random_hours(),
                'friday_hours': random_hours(),
                'saturday_hours': random.choice([random_hours(), None]),
            }

            Hours.objects.create(
                role=role,
                on_call=random.choice([True, False]),
                estimate_weekly_hours=f"{random.randint(30, 60)} hrs",
                job_description=fake.sentence(words=4),
                **work_days
            )
        
        def create_wages(role):
            wage_type = random.choice(['Hourly', 'Daily', 'Weekly', 'Monthly'])
            piece_rate_type = random.choice(['Hourly', 'Daily', 'Weekly', 'Monthly'])

            Wages.objects.create(
                role=role,
                wage=round(random.uniform(12, 50), 2),
                wage_type=wage_type,
                piece_rate_offerings=round(random.uniform(5, 30), 2) if random.choice([True, False]) else None,
                piece_rate_offerings_type=piece_rate_type,
                frequency_of_pay=random.choice(['Bi-weekly', 'Weekly', 'Monthly', 'Upon Completion']),
                details=random.choice([
                    "Includes bonuses and overtime",
                    "No deductions",
                    "Housing allowance included",
                    "Transportation covered",
                    None
                ])
            )


        def create_deduction(role):
            deduction_reasons = [
                "Housing cost",
                "Uniform and safety gear",
                "Transport fee",
                "Meal plan",
                "Background check fee",
                "Administrative fee"
            ]

            num_deductions = random.randint(0, 3)

            for _ in range(num_deductions):
                Deduction.objects.create(
                    role=role,
                    description=random.choice(deduction_reasons),
                    deduction_amount=round(random.uniform(10, 150), 2)
                )

        def create_qualifications(role):
            education_levels = [
                'None',
                'Highschool/GED',
                'Associates',
                'Bachelors',
                'Masters or higher',
                'Other degree'
            ]

            lifting_required = random.choice([True, False])
            support_employees = random.choice([True, False])

            Qualification.objects.create(
                role=role,
                minimum_education_requirement=random.choice(education_levels),
                experience_required=random.choice([
                    "General work experience",
                    "Industry-specific experience",
                    "Leadership experience",
                    "No experience required"
                ]),
                number_of_months_experience_required=random.randint(0, 36),
                training_required=random.choice([
                    "On-the-job training",
                    "Formal apprenticeship",
                    "Certification program",
                    "No formal training"
                ]),
                number_of_months_training_required=random.randint(0, 12),
                certification_license_requirements=random.choice([True, False]),
                drug_screen=random.choice([True, False]),
                lifting_requirements=lifting_required,
                lifting_requirement_weight=random.randint(20, 100) if lifting_required else None,
                exposure_to_temperature=random.choice([True, False]),
                extensive_pushing_or_pulling=random.choice([True, False]),
                extensive_sitting_or_walking=random.choice([True, False]),
                frequent_stooping_or_bending_over=random.choice([True, False]),
                repetitive_movements=random.choice([True, False]),
                support_of_other_employees=support_employees,
                support_of_other_employees_number=random.randint(1, 5) if support_employees else None,
                other_qualifications=random.choice([
                    "Must be bilingual.",
                    "Requires computer literacy.",
                    "Ability to operate heavy machinery.",
                    None
                ])
            )
        
        def create_employment_location(role):
            EmploymentLocation.objects.create(
                role=role,
                address=fake.street_address(),
                city=fake.city(),
                county=fake.city_suffix(),  # Not perfect, but Faker doesn't have a county field by default
                state=fake.state_abbr(),
                postal_code=fake.postcode(),
                additional_info=random.choice([
                    "Near public transport.",
                    "Remote site — vehicle required.",
                    "Overtime may be required during harvest season.",
                    None
                ])
            )
        
        def create_housing_info(role):
            HousingInformation.objects.create(
                role=role,
                address=fake.street_address(),
                city=fake.city(),
                county=fake.city_suffix(),
                state=fake.state_abbr(),
                postal_code=fake.postcode(),
                type_of_housing=random.choice(['Employer provided', 'Rental or Public']),
                additional_info=random.choice([
                    "Shared housing with other workers.",
                    "Private room included.",
                    "Short walk to job site.",
                    "Must provide own bedding.",
                    None
                ])
            )
        
        def create_meal_proovision(role):
            provides_meals = random.choice([True, False])
            MealProvision.objects.create(
                role=role,
                will_provide_meals=provides_meals,
                meal_charge_amount=round(random.uniform(2.00, 15.00), 2) if provides_meals else None,
                additional_info=random.choice([
                    "3 meals a day provided.",
                    "Vegetarian options available.",
                    "Meals provided only during weekdays.",
                    "No meal provision — bring your own.",
                    None
                ])
            )
        
        
        def create_roles(work_request):
            role = Role.objects.create(
                title=fake.job(),
                usdol_case_number=fake.bothify(text='A#####'),
                number_of_required_workers=random.randint(1, 10),
                description=fake.sentence(words=3),
                work_type=random.choice(['Full-time', 'Part-time', 'Temporary', 'Seasonal']),
                work_request=work_request
            )
            
            create_hours(role)
            create_wages(role)
            create_deduction(role)
            create_qualifications(role)
            create_employment_location(role)
            create_housing_info(role)
            create_meal_proovision(role)
        
        
        def start_job_order_creation(self):
            print("Creating job orders")
            employers = Organization.objects.filter(type='employer')
            
            if not employers.exists():
                print("No employers found")
                return
            STATUS_CHOICES = ['Draft', 'Requested', 'Open', 'Closed']
            
            print('Creating job orders and roles')
            for item in employers:
                for _ in range(10):
                    employer = item
                    start_date = fake.date_between(start_date='-30d', end_date='+30d')
                    end_date = start_date + timedelta(days=random.randint(7, 60))

                    work_request = WorkRequests.objects.create(
                        name=fake.job(),
                        start_date=start_date,
                        end_date=end_date,
                        required_workers=random.randint(5, 50),
                        employer=employer,
                        status=random.choice(STATUS_CHOICES)
                    )
                    
                    for _ in range(3):
                        create_roles(work_request)
                            
        start_job_order_creation(self);
        print('Job orders created successfully')
    
    def create_work_experiences(self):
        def create_experiences(user):
            for _ in range(2):
                start_date = fake.date_between(start_date='-5y', end_date='-1y')
                currently_working = random.choice([True, False])
                end_date = None if currently_working else start_date + timedelta(days=random.randint(180, 720))

                work_experience = UserWorkExperience.objects.create(
                    user=user,
                    country=fake.country(),
                    state=fake.state(),
                    visa_type=random.choice(["H-2A", "H-2B", "Other"]),
                    company=fake.company(),
                    start_date=start_date,
                    currently_working=currently_working,
                    end_date=end_date,
                    work_title=fake.job(),
                    supervisor_name=fake.name(),
                    supervisor_tel=fake.phone_number(),
                    supervisor_email=fake.email(),
                    work_under_h2a_in_usa=random.choice(['Yes', 'No'])
                )
                
                create_job_details
        
        def create_job_details(work_experience):
            job_types = [
                'Animals', 'Construction', 'Crop And Horticulture',
                'Licensed Vehicle Operation', 'Mechanics',
                'Work Supervsion/Management', 'Other'
            ]

            for _ in range(random.randint(1, 3)):  # Create 1–3 job details per experience
                job_type = random.choice(job_types)
                type_detail = random.choice([
                    'Asses', 'Bess', 'Camels', 'Apples',
                    'Apricots', 'Bananas', 'Cherries'])

                job_experience = UserJobExperience.objects.create(
                    user=work_experience.user,
                    work_experience=work_experience,
                    job_type=job_type,
                    type_details=type_detail
                )
                
                # Create experience details
                create_experience_details(job_experience)
            
        
        def create_experience_details(job_experience):
            details =  [
                'responsiblities', 'explanation', 'license',
                'evidence', 'visa', 'explanation_video'
            ]
            for item in details:
                value, is_attachment = '', False
                if item == 'responsiblities':
                    value = random.choice([
                        'Breeding', 'Caring', 'Packaging', 'Processing',
                        'Harvesting', 'Planting', 'Cultivating', 'Farming'
                    ])                
                elif item == 'explanation':
                    value = fake.sentence(nb_words=3)
                
                elif item == 'license':
                    is_attachment = True
                    value = '/uploads/samples/sample_license.jpg'
                elif item == 'evidence':
                    is_attachment = True
                    value = '/uploads/samples/sample_evidence.jpg'
                elif item == 'visa':
                    is_attachment = True
                    value = '/uploads/samples/sample_visa.webp'
                elif item == 'explanation_video':
                    is_attachment = True
                    value = '/uploads/samples/sample_video.mp4'
                    
                
                
            UserJobExperienceDetails.objects.create(
                job_experience=job_experience,
                kind=item,
                value = value,
                is_attachment = is_attachment
            )

    
        
        def create_test_workers():
            print('Creating test workers')
            for _ in range(1):
                user = User.objects.create(
                    email=fake.email(),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    curp=fake.bothify(text='????######??????##'),
                    telephone=fake.phone_number(),
                    password=fake.password(),
                    address_line_1=fake.street_address(),
                    address_line_2=fake.street_address(),
                    address_line_3=fake.street_address(),
                    city=fake.city(),
                    gender=random.choice(['Male', 'Female'])
                )
                user.set_password(user.password)
                user.groups.add(Group.objects.get(name='worker'))
                user.save()
                
                create_experiences(user)
        # start the process of creating workers
        # each worker gets assigned 2 experiences 
        # each experience gets assigned job details and experience details
        create_test_workers()
