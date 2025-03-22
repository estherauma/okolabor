from django.test import TestCase
from recruiting.models import WorkRequests, Employer  # Import Employer model

class AssignWorkerTestCase(TestCase):
    def setUp(self):
        # Create an Employer instance (since employer is required)
        self.employer = Employer.objects.create(name="Test Employer")

        # Now create WorkRequests with employer assigned
        self.work_request1 = WorkRequests.objects.create(
            name="Work Request 1", 
            start_date="2025-03-22", 
            required_workers=2,
            employer=self.employer  # Provide employer instance
        )
    
    def test_work_request_creation(self):
        self.assertEqual(self.work_request1.employer, self.employer)
