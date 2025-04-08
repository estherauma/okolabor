from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from account.models import User
from decouple import config

# faker
from faker import Faker
from recruiting.models import Hours, Organization, Role, Wages, WorkRequests
import random
fake = Faker()


class Command(BaseCommand):
    help = 'Create test data'

    def handle(self, *args, **options):
        print('Creating organizations')
        self.create_organizations()
        print('Test organizations created successfully')

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
                    description=fake.paragraph(nb_sentences=3),
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
                    description=fake.paragraph(nb_sentences=3),
                    is_active=True,
                    is_verified=random.choice([True, False]),
                    type='recruiter'
                )
            # Start to create Job Orders
            self.create_job_orders()
        create_employers()
        create_recruiters()
    
    def create_job_orders(self):
        
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
                job_description=fake.paragraph(nb_sentences=4),
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


        def create_deduction(roles):
            pass

        def create_qualifications(role):
            pass
        
        def create_employmentLocation(role):
            pass
        
        def create_housing_info(role):
            pass
        
        def create_meal_proovision(role):
            pass
        
        
        def create_roles(work_request):
            role = Role.objects.create(
                title=fake.job(),
                usdol_case_number=fake.bothify(text='A#####'),
                number_of_required_workers=random.randint(1, 10),
                description=fake.paragraph(nb_sentences=3),
                work_type=random.choice(['Full-time', 'Part-time', 'Temporary', 'Seasonal']),
                work_request=work_request
            )
            
            create_hours(role)
            create_wages(role)
            create_deduction(role)
            create_qualifications(role)
            create_employmentLocation(role)
            create_housing_info(role)
            create_meal_proovision(role)
            
            
        
        def start_job_order_creation(self):
            print("Creating job orders")
            employers = Organization.objects.filter(type='employer')
            
            if not employers.exists():
                print("No employers found")
                return
            STATUS_CHOICES = ['Draft', 'Requested', 'Open', 'Closed']
            
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
    
    def create_work_experiences(self):
        def create_experiences(self):
            pass
        
        def create_job_details(self):
            pass
        
        def create_experience_details(self):
            pass
        
        pass   
