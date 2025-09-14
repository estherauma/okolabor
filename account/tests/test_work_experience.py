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
        
    def test_get_user_work_experience_success(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        experiences = UserWorkExperience.objects.filter(user=self.user)
        serializer = UserWorkexperienceSerializer(experiences, many=True)
        self.assertEqual(response.data, serializer.data)
        
    def test_get_nonexistent_user(self):
        nonexistent_url = reverse('account:api-work-experience', kwargs={'user_id': 9999})
        response = self.client.get(nonexistent_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'No User matches the given query.')
       
    def test_post_user_work_experience_success(self):
        data = {
            "company": "Company 3",
            "work_title": "Designer",
            "start_date": "2023-06-01",
            "end_date": "2024-06-01",
            "type_of_work": "Farmal job"

        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(
            UserWorkExperience.objects.filter(
                user=self.user,
                company=data["company"],
                work_title=data["work_title"],
                start_date=data["start_date"],
                end_date=data["end_date"]
            ).exists()
        )
        
    def test_post_duplicate_user_work_experience(self):
        data = {
            "company": "Company 1",
            "work_title": "Developer",
            "start_date": "2022-01-01",
            "end_date": "2022-12-31",
            "type_of_work": "Farmal job"
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)
        self.assertEqual(
            response.data['message'],
            'User experience with given information already exists'
        )
        
    def test_post_invalid_user_work_experience(self):
        data = {
            "company": "",
            "position": "Tester",
            "start_date": "invalid-date",
            "end_date": ""
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('company', response.data)
        self.assertIn('start_date', response.data)
               
    def test_post_invalid_user_id(self):
        invalid_url = reverse('account:api-work-experience', kwargs={'user_id': 9999})
        data = {
            "company": "Company 4",
            "work_title": "Engineer",
            "start_date": "2023-06-01",
            "end_date": "2024-06-01"
        }
        response = self.client.post(invalid_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'No User matches the given query.')
