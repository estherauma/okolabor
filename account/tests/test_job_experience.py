from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from account.models import User, UserJobExperience, UserWorkExperience

class UserJobExperienceViewTest(APITestCase):
    def setUp(self):
    
        self.user = User.objects.create_user(
            curp="CURP1234567890ABC",
            email="testuser@example.com",
            password="testpass123",
            telephone="1234567890"
        )

        self.work_experience = UserWorkExperience.objects.create(
            user=self.user,
            company="Tech Corp",
            work_title="Software Developer",
            start_date="2023-01-01",
            end_date="2023-12-31"
        )

        self.existing_experience = UserJobExperience.objects.create(
            user=self.user,
            job_type="Full Time",
            type_details="Remote",
            work_experience=self.work_experience
        )

        self.client = APIClient()
        self.url = reverse('account:api-job-experience', kwargs={'user_id': self.user.id})
        
    def test_get_job_experiences_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['job_type'], 'Full Time')
        
    def test_get_job_experiences_no_experiences(self):
        UserJobExperience.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
        
    def test_update_job_experience_invalid_experience(self):
        data = {"experience_id": 999, "job_type": "Updated"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_post_user_job_experience_duplicate(self):
      
        data = {
            "work_experience_id": self.work_experience.id,
            "job_type": "Full Time",
            "type_details": "Remote"
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Job experience already exists", response.data['message'])
        
    def test_post_user_job_experience_invalid_data(self):
        data = {
            "work_experience_id": "", 
            "job_type": "Contract"
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("No UserWorkExperience matches the given query", str(response.data))