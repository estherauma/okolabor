from django.test import TestCase, Client
from django.urls import reverse
from recruiting.models import WorkRequests, Organization, WorkAssignment, Role, User
from django.contrib.auth.models import Group

class AssignWorkerViewTestCase(TestCase):
    def setUp(self):
        """Set up the test environment before each test."""
        # Create an employer instance
        self.employer = Organization.objects.create(name="Test Employer")

        # Create a WorkRequest instance
        self.work_request = WorkRequests.objects.create(
            name="Test Work Request",
            start_date="2025-03-22",
            required_workers=2,
            employer=self.employer,
            status="Open"
        )

        # Create a Role instance
        self.role = Role.objects.create(
            title="Test Role",
            usdol_case_number="12345",
            number_of_required_workers=1,
            description="Test Role Description",
            work_type="Full Time",
            work_request=self.work_request
        )

        # Create a User instance
        self.worker_group = Group.objects.create(name='worker')
        self.user = User.objects.create_user(
            curp='TEST1234567890',
            email='test@example.com',
            password='password',
            first_name='Test',
            last_name='User'
        )
        self.user.groups.add(self.worker_group)

        self.client = Client()

    def test_assign_worker_view_post_success(self):
        """Test the POST request for AssignWorkerView with valid data."""
        url = reverse('recruiting_web:assign_worker')  # Adjust the URL name as per your configuration
        data = {
            'worker_ids': self.user.id,
            'work_request': self.work_request.id,
            'role': self.role.id,
            'status': 'Assigned'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Expecting a redirect
        self.assertTrue(WorkAssignment.objects.filter(worker=self.user, role=self.role, work_request=self.work_request).exists())

    def test_assign_worker_view_post_missing_data(self):
        """Test the POST request for AssignWorkerView with missing data."""
        url = reverse('recruiting_web:assign_worker')  # Adjust the URL name as per your configuration
        data = {
            'worker_ids': '',  # Missing worker IDs
            'work_request': self.work_request.id,
            'role': self.role.id,
            'status': 'Assigned'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'success': False, 'message': 'Missing data'})

    def test_assign_worker_view_post_invalid_role(self):
        """Test the POST request for AssignWorkerView with an invalid role."""
        url = reverse('recruiting_web:assign_worker')  # Adjust the URL name as per your configuration
        data = {
            'worker_ids': self.user.id,
            'work_request': self.work_request.id,
            'role': 99999,  # Invalid role ID
            'status': 'Assigned'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'success': False, 'message': 'Invalid work requests or roles'})

    def test_assign_worker_view_post_invalid_role(self):
        """Test the POST request for AssignWorkerView with an invalid role."""
        url = reverse('recruiting_web:assign_worker')  # Adjust the URL name as per your configuration
        data = {
            'worker_ids': self.user.id,
            'work_request': self.work_request.id,
            'role': 99999,  # Invalid role ID
            'status': 'Assigned'
        }
        response = self.client.post(url, data)
        
        # Check if response returns a 400 status code
        self.assertEqual(response.status_code, 400)

        # Assert that the error message contains "No Role matches the given query."
        response_json = response.json()
        self.assertIn("message", response_json)
        self.assertIn("No Role matches the given query.", response_json["message"])
