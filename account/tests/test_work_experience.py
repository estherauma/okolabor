from rest_framework.test import APITestCase,APIClient
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from account.models import User, UserWorkExperience
from account.serializers import UserWorkexperienceSerializer

User = get_user_model()

class UserWorkExperienceViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            curp='CURP123456HRDACV54',
            email= 'test@fiftyeight.io',
            password='Testing321123'
        )
        
        self.experience1 = UserWorkExperience.objects.create(
            user=self.user,
            company="Company 1",
            work_title="Developer",
            start_date="2022-01-01",
            end_date="2022-12-31"
        )
        
        self.experience2 = UserWorkExperience.objects.create(
            user=self.user,
            company="Company 2",
            work_title="QA",
            start_date="2023-01-01",
            end_date="2023-12-31"
        )
        
        self.url = reverse('account:api-work-experience', kwargs={'user_id': self.user.id})
        
    def test_get_user_work_experience(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        experiences = UserWorkExperience.objects.filter(user=self.user)
        serializer = UserWorkexperienceSerializer(experiences, many=True)
        self.assertEqual(response.data, serializer.data)
