from django.test import TestCase
from recruiting.models import WorkRequests, Employer
from datetime import date

class WorkRequestsTestCase(TestCase):
    def setUp(self):
        """Set up the test environment before each test."""
        # Create an employer instance to avoid null constraint error
        self.employer = Employer.objects.create(name="Test Employer")

        # Create a WorkRequest instance using the employer
        self.work_request = WorkRequests.objects.create(
            name="Test Work Request",
            start_date=date(2025, 3, 22),
            end_date=date(2025, 3, 22),
            required_workers=2,
            employer=self.employer,  # Assign employer to prevent IntegrityError
            status="Open"
        )

    def test_work_request_creation(self):
        """Test if the work request is created successfully."""
        work_request = WorkRequests.objects.get(name="Test Work Request")
        self.assertEqual(work_request.name, "Test Work Request")
        self.assertEqual(work_request.required_workers, 2)
        self.assertEqual(work_request.employer, self.employer)
        self.assertEqual(work_request.status, "Open")

    def test_work_request_str_representation(self):
        """Test the string representation of the WorkRequests model."""
        self.assertEqual(str(self.work_request), "Test Work Request")
