from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Group
from recruiting.models import Organization, EmployerRecruiter, User
from django.contrib.messages import get_messages

class RecruiterListViewTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(curp='admin_curp', email='admin@example.com', password='password')
        self.recruiter_admin_group = Group.objects.create(name='recruiter_admin')
        self.admin_user.groups.add(self.recruiter_admin_group)

        self.recruiter_user = User.objects.create_user(curp='recruiter_curp', email='recruiter@example.com', password='password')
        self.recruiter_group = Group.objects.create(name='recruiter')
        self.recruiter_user.groups.add(self.recruiter_group)

        self.employer = Organization.objects.create(name='Test Employer')
        EmployerRecruiter.objects.create(employer=self.employer, recruiter=self.recruiter_user)

    def test_access_denied_for_non_admin(self):
        self.client.login(curp='recruiter_curp', password='password')
        response = self.client.get(reverse('recruiting_web:recruiter_list'))
        self.assertRedirects(response, reverse('recruiting_web:access_denied'))

    def test_recruiter_list_view(self):
        self.client.login(curp='admin_curp', password='password')
        response = self.client.get(reverse('recruiting_web:recruiter_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('recruiters', response.context)
        self.assertIn('employers', response.context)

class AddRecruiterToEmployerViewTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(curp='admin_curp', email='admin@example.com', password='password')
        self.recruiter_admin_group = Group.objects.create(name='recruiter_admin')
        self.admin_user.groups.add(self.recruiter_admin_group)

        self.recruiter_user = User.objects.create_user(curp='recruiter_curp', email='recruiter@example.com', password='password')
        self.recruiter_group = Group.objects.create(name='recruiter')
        self.recruiter_user.groups.add(self.recruiter_group)

        self.employer = Organization.objects.create(name='Test Employer')

    def test_add_recruiter_to_employer(self):
        self.client.login(curp='admin_curp', password='password')
        response = self.client.post(reverse('recruiting_web:add_recruiter_to_employer', args=[self.employer.id, self.recruiter_user.id]))
        self.assertRedirects(response, reverse('recruiting_web:recruiter_list'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f"Recruiter {self.recruiter_user.email} assigned to {self.employer.name}.")

    def test_add_recruiter_already_assigned(self):
        EmployerRecruiter.objects.create(employer=self.employer, recruiter=self.recruiter_user)
        self.client.login(curp='admin_curp', password='password')
        response = self.client.post(reverse('recruiting_web:add_recruiter_to_employer', args=[self.employer.id, self.recruiter_user.id]))
        self.assertRedirects(response, reverse('recruiting_web:recruiter_list'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f"Recruiter {self.recruiter_user.email} is already assigned to {self.employer.name}.")

class RemoveRecruiterFromEmployerViewTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(curp='admin_curp', email='admin@example.com', password='password')
        self.recruiter_admin_group = Group.objects.create(name='recruiter_admin')
        self.admin_user.groups.add(self.recruiter_admin_group)

        self.recruiter_user = User.objects.create_user(curp='recruiter_curp', email='recruiter@example.com', password='password')
        self.recruiter_group = Group.objects.create(name='recruiter')
        self.recruiter_user.groups.add(self.recruiter_group)

        self.employer = Organization.objects.create(name='Test Employer')
        self.employer_recruiter = EmployerRecruiter.objects.create(employer=self.employer, recruiter=self.recruiter_user)

    def test_remove_recruiter_from_employer(self):
        self.client.login(curp='admin_curp', password='password')
        response = self.client.post(reverse('recruiting_web:remove_recruiter_from_employer', args=[self.employer.id, self.recruiter_user.id]))
        self.assertRedirects(response, reverse('recruiting_web:recruiter_list'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f"Recruiter {self.recruiter_user.email} removed from {self.employer.name}.")

    def test_remove_recruiter_already_removed(self):
        self.employer_recruiter.delete()
        self.client.login(curp='admin_curp', password='password')
        response = self.client.post(reverse('recruiting_web:remove_recruiter_from_employer', args=[self.employer.id, self.recruiter_user.id]))
        self.assertRedirects(response, reverse('recruiting_web:recruiter_list'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f"Recruiter {self.recruiter_user.email} removed from {self.employer.name}.")
