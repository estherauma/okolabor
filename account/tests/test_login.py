import json
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from account.models import User
from account.jwt_manager import JwtManager
from django.test.testcases import TestCase
from rest_framework.test import APITestCase
from account.models import User, UserWorkExperience
from account.models import UserPreference
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
class LoginAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('account:api-login')

        # Create a test user
        self.user = User.objects.create_user(
            curp='HEGJ820506HBCRRN09',
            email='test@example.com',
            password='testPassword1',
            is_verified=True,
            telephone='+999752466601'
        )

    def test_login_valid_credentials(self):
        # Prepare valid login credentials
        data = {
            'identifier': 'test@example.com',
            'password': 'testPassword1'
        }

        # Send POST request to login API
        response = self.client.post(self.login_url, data, format='json')

        # Assert response status code and token
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('data', response.data)

        # Verify the token
        token = response.data['token']
        identity_manager = JwtManager()
        decoded_payload = identity_manager.decode(token)

        # Assert the decoded payload
        self.assertEqual(decoded_payload['email'], self.user.email)
        self.assertEqual(decoded_payload['id'], self.user.pk)
        self.assertEqual(decoded_payload['firstName'], self.user.first_name)
        self.assertEqual(decoded_payload['lastName'], self.user.last_name)
        self.assertEqual(decoded_payload['isAdmin'], self.user.is_admin)
        self.assertEqual(decoded_payload['roles'], [])

    def test_login_invalid_credentials(self):
        # Prepare invalid login credentials
        data = {
            'identifier': 'test@example.com',
            'password': 'wrongpassword'
        }

        # Send POST request to login API
        response = self.client.post(self.login_url, data, format='json')

        # Assert response status code and error message
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Invalid credentials')

    def test_login_nonexistent_user(self):
        # Prepare login credentials for a nonexistent user
        data = {
            'identifier': 'nonexistent@example.com',
            'password': 'testpassword'
        }

        # Send POST request to login API
        response = self.client.post(self.login_url, data, format='json')

        # Assert response status code and error message
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_unverified_account(self):
        # Create an unverified user
        unverified_user = User.objects.create_user(
            curp='HEGJ820506HBCRRN10',
            email='unverified@example.com',
            password='testpassword',
            telephone='+999752466602',
            is_verified=False
        )

        # Prepare login credentials for the unverified user
        data = {
            'identifier': 'unverified@example.com',
            'password': 'testpassword'
        }

        # Send POST request to login API
        response = self.client.post(self.login_url, data, format='json')

        # Assert response status code and error message
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Account not verified')

    def test_login_invalid_request(self):
        # Send POST request to login API without any data
        response = self.client.post(self.login_url, format='json')

        # Assert response status code and error message
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('identifier', response.data)
        self.assertIn('password', response.data)

class LoginTestCase(TestCase):
    def setUp(self):
        # Ensure the group with ID 1 exists
        group, created = Group.objects.get_or_create(id=1, name="recruiter")

        # Create a test user and add to the group
        self.user = User.objects.create_user(
            email="test@okolabor.io",
            password="adminwert1A"
        )
        self.user.groups.add(group)  # Add user to group
        self.user.save()
        
        
    def test_login_template(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ltr/login.html')

    def test_login_success(self):
        response = self.client.post('/', {
            'email': 'samsonkapeyi@fiftyeight.io',
            'password': 'adminwert1A'}
        )
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, '/index/')
        
    
    def test_login_invalid_password(self):
        response = self.client.post('/', {
            'email': 'test@example.com',
            'password': 'testPassword'})
        self.assertEquals(response.status_code, 200)

    def test_login_invalid_email(self):
        response = self.client.post('/', {
            'email': 'test',
            'password': 'testPassword1'})
        self.assertEquals(response.status_code, 200)

    

class RegisterTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
    def test_register_template(self):
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ltr/register.html')

    def test_register_success(self):
        response = self.client.post('/register', {
            'email': 'test@example.com',
            'password': 'testPassword1', })
        self.assertEquals(response.status_code, 200) 

    def test_register_invalid_email(self):
        response = self.client.post('/register', {
            'email': 'test',
            'password': 'testPassword1'})
        self.assertEquals(response.status_code, 200)

    def test_register_invalid_password(self):
        response = self.client.post('/register', {
            'email': 'test@example.com',
            'password': 'test'})
        self.assertEquals(response.status_code, 200)

class UserWorkExperienceViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test@example.com', curp='XYZ789', password='testPassword1', is_active=True, is_verified=True)
        self.url = reverse('account:api-work-experience', args=[self.user.pk])  
        self.experience = UserWorkExperience.objects.create(
            user=self.user,
            company='Test Company',
            start_date='2024-01-01',
            end_date='2024-12-31',
           
        )
        
    def test_get_user_work_experience(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['company'], 'Test Company')

    

    def test_get_non_existent_user_work_experience(self):
        url = reverse('account:api-work-experience', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    
    def test_create_user_work_experience_invalid_data(self):
        data = {
            'company': '',
            'start_date': '2023-01-01',
            'end_date': '2023-12-31',
            'role': 'Developer'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_work_experience_invalid_start_date(self):
        data = {
            'company': 'Test Company',
            'start_date': '2025-01-01',
            'end_date': '2025-12-31',
            'role': 'Developer'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_work_experience_invalid_end_date(self):
        data = {
            'company': 'Test Company',
            'start_date': '2024-01-01',
            'end_date': '2023-12-31',
            'role': 'Developer'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_work_experience_invalid_role(self):
        data = {
            'company': 'Test Company',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'role': ''
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    

   

    

    def test_create_user_work_experience_non_existent_user(self):
        url = reverse('account:api-work-experience', args=[999])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    
class UserPreferencesUpdateViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test@example.com', curp='XYZ789', password='testPassword1', is_active=True, is_verified=True)
        self.url = reverse('account:update-user-preferences', args=[self.user.pk])
        self.preference = UserPreference.objects.create(
            user=self.user,
            key='theme',
            value='dark',
            kind='preference'
        )

    def test_get_user_preferences(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['key'], 'theme')
        self.assertEqual(response.data[0]['value'], 'dark')
        self.assertEqual(response.data[0]['kind'], 'preference')

    def test_get_user_preferences_with_kind(self):
        url = f"{self.url}?kind=preference"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['key'], 'theme')
        self.assertEqual(response.data[0]['value'], 'dark')
        self.assertEqual(response.data[0]['kind'], 'preference')

    def test_get_non_existent_user_preferences(self):
        url = reverse('account:update-user-preferences', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_user_preferences(self):
        data = {
            'preferences': [
                {
                    'key': 'language',
                    'value': 'es',
                    'kind': 'preference'
                }
            ]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[1]['key'], 'language')
        self.assertEqual(response.data[1]['value'], 'es')
        self.assertEqual(response.data[1]['kind'], 'preference')

    def test_create_user_preferences_invalid_data(self):
        data = {
            'preferences': [
                {
                    'key': 'language',
                    'value': 'es',
                    'kind': 'preference'
                },
                {
                    'key': '',
                    'value': 'dark',
                    'kind': 'preference'
                }
            ]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_create_user_preferences_invalid_kind(self):
        data = {
            'preferences': [
                {
                    'key': 'language',
                    'value': 'es',
                    'kind': 'invalid'
                }
            ]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)
        
    def test_create_user_preferences_invalid_key(self):
        data = {
            'preferences': [
                {
                    'key': '',
                    'value': 'es',
                    'kind': 'preference'
                }
            ]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)


    def test_create_user_preferences_non_existent_user(self):
        url = reverse('account:update-user-preferences', args=[999])
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, 404)

    def test_create_user_preferences_non_existent_key(self):
        data = {
            'preferences': [
                {
                    'key': 'invalid',
                    'value': 'es',
                    'kind': 'preference'
                }
            ]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_create_user_preferences_non_existent_kind(self):
        data = {
            'preferences': [
                {
                    'key': 'language',
                    'value': 'es',
                    'kind': 'invalid'
                }
            ]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_create_user_preferences_non_existent_value(self):
        data = {
            'preferences': [
                {
                    'key': 'language',
                    'value': 'invalid',
                    'kind': 'preference'
                }
            ]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_create_user_preferences_invalid_data(self):
        data = {
            'preferences': [
                {
                    'key': 'invalid',
                    'value': 'invalid',
                    'kind': 'invalid'
                }
            ]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)

    

    



    