from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from account.models import UserReportedProblem 

User = get_user_model()
class TestReportproblems(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            curp="testusercurp",
            email="testuser@example.com",
            password="testpassword"
        )
        self.url = reverse("account:api-report-problem", args=[self.user.id])

        
    def test_report_problem_success(self):
        data = {
            "topic": "App Issue",
            "description": "I am facing an issue with the app",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK) 
        self.assertEqual(UserReportedProblem.objects.count(), 1) 
        
        problem = UserReportedProblem.objects.get()
        self.assertEqual(problem.topic, "App Issue") 
        self.assertEqual(problem.description, "I am facing an issue with the app")