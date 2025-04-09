from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from account.models import User
from decouple import config

class Command(BaseCommand):
    help = 'Create test credentials'

    def handle(self, *args, **options):
        print('Creating default user groups')
        self.create_roles()
        self.create_users()
        print('Test credentials created')

    def create_roles(self):
        roles = ['worker', 'recruiter', 'employer', 'admin', 'recruiter_admin', 'employer_admin']
        for role_name in roles:
            role, created = Group.objects.get_or_create(name=role_name)
            if created:
                self.stdout.write(f'Role "{role_name}" created.')
            else:
                self.stdout.write(f'Role "{role_name}" already exists.')

    def create_users(self):
        users = [
            {
                'email': 'testworker@okolabor.com',
                'curp': 'HEGJ820506HBCRRN50',
                'telephone': '+999752466600'
            },
            {
                'email': 'testadmin@okolabor.com',
                'curp': 'HEGJ820506HBCRRN51',
                'telephone': '+999752466601'
            },
            {
                'email': 'testrecruiter@okolabor.com',
                'curp': 'HEGJ820506HBCRRN52',
                'telephone': '+999752466602'
            },
            {
                'email': 'testrecruiteradmin@okolabor.com',
                'curp': 'HEGJ820506HBCRRN53',
                'telephone': '+999752466603'
            },
            {
                'email': 'testemployer@okolabor.com',
                'curp': 'HEGJ820506HBCRRN54',
                'telephone': '+999752466604'
            },
            {
                'email': 'testemployeradmin@okolabor.com',
                'curp': 'HEGJ820506HBCRRN55',
                'telephone': '+999752466605'
            }
        ]

        for user_data in users:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                curp=user_data['curp'],
                telephone=user_data['telephone']
            )
            if created:
                self.stdout.write(f'User "{user_data["email"]}" created.')
            else:
                self.stdout.write(f'User "{user_data["email"]}" already exists.')

            if user_data['email'] == 'testworker@okolabor.com':
                user.groups.add(Group.objects.get(name='worker'))
            elif user_data['email'] == 'testadmin@okolabor.com':
                user.groups.add(Group.objects.get(name='admin'))
            elif user_data['email'] == 'testrecruiter@okolabor.com':
                user.groups.add(Group.objects.get(name='recruiter'))
            elif user_data['email'] == 'testrecruiteradmin@okolabor.com':
                user.groups.add(Group.objects.get(name='recruiter_admin'))
            elif user_data['email'] == 'testemployeradmin@okolabor.com':
                user.groups.add(Group.objects.get(name='employer_admin'))

            
            user.set_password(user_data['email'].split('@')[0] + config('TEST_ACCOUNT_PASSWORD'))
            user.save()
