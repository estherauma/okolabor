from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class UserAccountRecoveryResetTestCase(APITestCase):
   def setUp(self):
    self.user = User.objects.create_user(
        email='test@example.com',
        curp='TEST123456BVCXSD12',
        password='oldpassword123',
    )
    self.url = reverse('password-reset')
    
def test_valid_password_reset(self):
    data = {
        'reset_token': '9677', 
        'password': 'newpassword123'
    }
    response = self.client.post(self.url, data, format='json', HTTP_ACCEPT='application/json')

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    response_data = response.json()
    self.assertIn('message', response_data)
    self.assertEqual(response_data['message'], 'Password reset successfully.')

    self.user.refresh_from_db()
    self.assertTrue(self.user.check_password('newpassword123'))

    self.assertIsNone(self.user.reset_code)
    
def test_invalid_token(self):
        data = {
            'reset_token': 'invalid_token',
            'password': 'newpassword123'
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Not found.')
        
def test_invalid_password(self):
        data = {
            'reset_token': 'valid_reset_token',
            'password': 'short' 
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn('password', response.data)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('oldpassword123'))
