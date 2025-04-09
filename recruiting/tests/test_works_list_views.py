from django.test import TestCase, Client
from django.urls import reverse
from recruiting.models import WorkRequests, Organization, WorkAssignment, Role, User
from account.models import UserPreference
from django.contrib.auth.models import Group

class WorkerListViewTestCase(TestCase):
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
            first_name='Test',
            last_name='User',
            password='password'
        )
        self.user.groups.add(self.worker_group)

        # Create UserPreferences for the user
        for step in ["profileStepOne", "workExperienceList", "documentsStepOne"]:
            UserPreference.objects.create(user=self.user, key=step, value="True")

        self.client = Client()

    def test_worker_list_view_get(self):
        """Test the GET request for WorkerListView."""
        url = reverse('recruiting_web:workers')  # Adjust the URL name as per your configuration
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recruiting/workers/list.html')
        self.assertContains(response, 'Test User')

    def test_worker_list_view_post_success(self):
        """Test the POST request for WorkerListView with valid data."""
        url = reverse('recruiting_web:workers')  # Adjust the URL name as per your configuration
        data = {
            'worker_ids[]': [self.user.id],
            'work_request': [self.work_request.id],
            'role': [self.role.id],
            'status': 'Assigned'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': 'Workers assigned successfully!'})
        self.assertTrue(WorkAssignment.objects.filter(worker=self.user, role=self.role, work_request=self.work_request).exists())

    def test_worker_list_view_post_missing_data(self):
        """Test the POST request for WorkerListView with missing data."""
        url = reverse('recruiting_web:workers')  # Adjust the URL name as per your configuration
        data = {
            'worker_ids[]': [],
            'work_request': [],
            'role': [],
            'status': 'Assigned'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        expected_response = {'error': 'Invalid request, missing data'}
        self.assertJSONEqual(response.content, expected_response)

    def test_worker_list_view_post_invalid_role(self):
        """Test the POST request for WorkerListView with an invalid role."""
        url = reverse('recruiting_web:workers')  # Adjust the URL name as per your configuration
        data = {
            'worker_ids[]': [self.user.id],
            'work_request': [self.work_request.id],
            'role': [99999],  # Invalid role ID
            'status': 'Assigned'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        expected_response = {'error': 'Invalid work requests or roles'}
        self.assertJSONEqual(response.content, expected_response)

    def test_worker_list_view_post_invalid_work_request(self):
        """Test the POST request for WorkerListView with an invalid work request."""
        url = reverse('recruiting_web:workers')  # Adjust the URL name as per your configuration
        data = {
            'worker_ids[]': [self.user.id],
            'work_request': [99999],  # Invalid work request ID
            'role': [self.role.id],
            'status': 'Assigned'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        expected_response = {'error': 'Invalid work requests or roles'}
        self.assertJSONEqual(response.content, expected_response)

    def test_worker_list_view_profile_completion(self):
        """Test the profile completion calculation."""
        url = reverse('recruiting_web:workers')  # Adjust the URL name as per your configuration
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Check the context data directly
        workers = response.context['workers']
        self.assertTrue(hasattr(workers[0], 'profile_completion_percentage'))
        self.assertGreater(workers[0].profile_completion_percentage, 0)


    def test_worker_list_view_ajax_request(self):
        """Test the AJAX request for WorkerListView."""
        url = reverse('recruiting_web:workers')  # Adjust the URL name as per your configuration
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertIn('workers', response.json())
        self.assertIn('num_pages', response.json())
