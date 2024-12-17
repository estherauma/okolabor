from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from account.models import User, UserWorkExperience
from account.serializers import UserWorkexperienceSerializer

class UserWorkExperienceDetailsViewTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            curp="CURP123456ABCDEF76",
            email="testuser@example.com",
            password="testpass123",
            telephone="1234567890"
        )
        
        self.experience = UserWorkExperience.objects.create(
            user=self.user,
            company="ABC Corp",
            work_title ="Software Developer",
            start_date="2021-01-01",
            end_date="2023-01-01",
        )
        
        self.client = APIClient()
        self.url = reverse(
            'account:api-single-experience',
            kwargs={'user_id': self.user.id, 'experience_id': self.experience.id}
        )
        
    def test_get_work_experience_details_success(self):
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = UserWorkexperienceSerializer(self.experience)
        self.assertEqual(response.data, serializer.data)
