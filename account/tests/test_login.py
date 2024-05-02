import json
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from account.models import User
from account.jwt_manager import JwtManager

class LoginAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('account:api-login')

        # Create a test user
        self.user = User.objects.create_user(
            curp='HEGJ820506HBCRRN09',
            email='test@example.com',
            password='testPassword1',
            is_verified=True
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
