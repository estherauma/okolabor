from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from account.models import User
from decouple import config

# faker
from faker import Faker
from recruiting.models import Organization, WorkRequests
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

                    WorkRequests.objects.create(
                        name=fake.job(),
                        start_date=start_date,
                        end_date=end_date,
                        required_workers=random.randint(5, 50),
                        employer=employer,
                        status=random.choice(STATUS_CHOICES)
                    )
            
            
        
        def create_roles(self):
            pass
        pass
    
        start_job_order_creation(self);
    
    def create_work_experiences(self):
        def create_experiences(self):
            pass
        
        def create_job_details(self):
            pass
        
        def create_experience_details(self):
            pass
        
        pass   
