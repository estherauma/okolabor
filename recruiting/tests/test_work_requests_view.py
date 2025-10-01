from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import Group
from recruiting.models import Organization, WorkRequests, Role, WorkAssignment, Hours, Deduction, User
from recruiting.forms import WorkRequestForm


class WorkRequestCopyViewTest(TestCase):
    def setUp(self):
        # Create user and login
        self.user = User.objects.create_user(
            curp='TEST1234567800',
            email='test@example.com',
            password='password',
            first_name='Test',
            last_name='User'
        )
        self.group = Group.objects.create(name='admin')
        self.user.groups.add(self.group)
        self.client = Client()
        self.client.login(username=self.user.email, password='password')
        self.employer = Organization.objects.create(
            name="Test Org",
            type="employer",
            email="testemployer@example.com",
            phone="123456789",
            website="https://example.com",
            address="123 Main St",
            city="City",
            state="ST",
            country="Country",
            zip_code="12345",
            description="Test description"
        )
        self.work_request = WorkRequests.objects.create(
            name='Test WR',  
            start_date="2025-03-22",
            end_date="2025-04-22",
            required_workers=1,
            employer=self.employer,
            status="Open",
        )
        self.role = Role.objects.create(
            title="Test Role",
            usdol_case_number="12345",
            number_of_required_workers=2,
            description="Test Role Description",
            work_type="Full Time",
            work_request=self.work_request
        )
        self.hours = Hours.objects.create(
            role=self.role,
            estimate_weekly_hours="40",
            on_call=False,
            job_description="Test job description"
        )
        self.deduction = Deduction.objects.create(role=self.role, description='Test Deduction', deduction_amount=10)
        self.worker = User.objects.create_user(
            curp='TEST2344567800',
            email='worker@example.com',
            password='workerpass',
            first_name='worker',
            last_name='User'
        )
        worker_group = Group.objects.create(name='worker')
        self.worker.groups.add(worker_group)

    def test_copy_work_request_success(self):
        url = reverse('recruiting_web:workrequest_copy', args=[self.work_request.pk])
        data = {
            'name': 'Test WR',  
            'start_date': '2025-05-01',
        }
        for field in WorkRequestForm().fields:
            if field not in data:
                value = getattr(self.work_request, field, '')
                if hasattr(value, 'id'):
                    value = value.id
                data[field] = value
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WorkRequests.objects.count(), 2)

        new_wr = WorkRequests.objects.exclude(pk=self.work_request.pk).first()
        self.assertTrue(new_wr.name.endswith('(Copy)'))
        self.assertEqual(new_wr.roles.count(), 1)
        new_role = new_wr.roles.first()
        self.assertTrue(hasattr(new_role, 'hours'))
        self.assertEqual(new_role.hours.estimate_weekly_hours, '40')
        self.assertEqual(new_role.deductions.count(), 1)
        self.assertEqual(WorkAssignment.objects.filter(work_request=new_wr, role=new_role).count(), 1)

    def test_copy_work_request_invalid_form(self):
        url = reverse('recruiting_web:workrequest_copy', args=[self.work_request.pk])
        data = {} 
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WorkRequests.objects.count(), 1)