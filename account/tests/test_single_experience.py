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
        
    def test_get_work_experience_details_not_found(self):
        
        url = reverse('account:api-single-experience', 
                      kwargs={'user_id': self.user.id, 'experience_id': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_patch_work_experience_success(self):
        
        updated_data = {
            "company": "XYZ Corp",
            "work_title": "Senior Developer"
        }
        response = self.client.patch(self.url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.experience.refresh_from_db()
        self.assertEqual(self.experience.company, "XYZ Corp")
        self.assertEqual(self.experience.work_title, "Senior Developer")
        
    def test_patch_work_experience_invalid_data(self):
        
        invalid_data = {
            "start_date": "invalid-date-format"  
        }
        response = self.client.patch(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
