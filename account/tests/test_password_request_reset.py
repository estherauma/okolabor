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
        
    def test_post_invalid_email(self):
        response = self.client.post(self.url, self.invalid_payload)  
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        
    def test_post_missing_email(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_post_email_not_found(self):
        response = self.client.post(self.url, self.invalid_payload)  
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        
    @patch('random.randrange', return_value='12345')
    def test_post_passwords_do_not_match(self, mock_random):
        self.client.post(self.url, self.valid_payload)
        
        reset_url = reverse('account:password-request-reset')
        mismatched_password_payload = {
            'reset_code': '12345',  
            'new_password': 'newpassword123',
            'confirm_password': 'password123'
        }
        response = self.client.post(reset_url, mismatched_password_payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
       
    @patch('random.randrange', return_value='12345')
    def test_post_invalid_token(self, mock_random):
        self.client.post(self.url, self.valid_payload)

        reset_url = reverse('account:password-request-reset')
        invalid_token_payload = {
            'reset_code': 'wrongtoken', 
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        response = self.client.post(reset_url, invalid_token_payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
