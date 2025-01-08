from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.urls import reverse

User= get_user_model()
class UserAccountRecoveryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url =reverse('account:password-request-reset') 
        self.user = User.objects.create_user(
            curp="NBCD654321NBVDES23",
            email="testuser@example.com",
            password="testpassword"
        )
        self.valid_payload = {'email': 'testuser@example.com'}
        self.invalid_payload = {'email': 'nonexistent@example.com'}

    @patch('random.randrange', return_value='12345')
    @patch('common.email.EmailHelper.send_email')
    def test_post_valid_email(self, mock_send_email, mock_random):
        
        response = self.client.post(self.url, self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(
            response.data['message'],
            'Please check your email for the password reset code.'
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.reset_code, '12345')
        mock_send_email.assert_called_once_with(
            to_emails=['testuser@example.com'],
            subject='Restablece tu contraseña de okolabor',
            body={
                'correo_electrónico': 'testuser@example.com',
                'token_rest_contraseña': '12345',
            }
        )
        
    

   