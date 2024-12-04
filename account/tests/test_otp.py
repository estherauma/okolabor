from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
import os

User = get_user_model()

class GetOTPTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            curp='CURP123456HRDACV54',
            email='testuser@example.com',
            password='Testing321123',
            first_name='Test',
            last_name='User',
            telephone='+256123456789'
        )
        self.user_id = str(self.user.id)
        self.client.force_authenticate(user=self.user)
        self.url = reverse('account:otp-generate')

        
    @patch('account.serializers.OTPVerification.send_otp')   
    def test_generate_otp_failure(self, mock_send_otp):
        mock_send_otp.return_value = {"error": "Invalid phone number format"}
        phone_number = "256123456789" 
        data = {
            "user_id": str(self.user.id),
            "phone_number": phone_number
        }

        response = self.client.post(self.url, data)
        print(response.data)
        self.assertEqual(response.status_code, 400)
        
    @patch.dict(os.environ, {
        "TWILIO_ACCOUNT_SID": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", 
        "TWILIO_AUTH_TOKEN": "fake_auth_token",                     
        "TWILIO_PHONE_NUMBER": "+1234567890" ,
        "TWILIO_VERIFY_SID": "VAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"                       
    })  
    @patch('account.serializers.OTPVerification.send_otp')
    def test_generate_otp_success(self, mock_send_otp):
        mock_send_otp.return_value = 'pending'
        phone_number = "+256123456780" 
        data = {
            "user_id": str(self.user.id),
            "phone_number": phone_number
        }

        response = self.client.post(self.url, data)
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "pending"})
        self.user.refresh_from_db()
        self.assertEqual(self.user.telephone, phone_number)
        
    def test_generate_otp_invalid_input(self):
        data = {
            "phone_number": "256123456789"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("user_id", response.data)
        
    def test_generate_otp_nonexistent_user(self):
        data = {
            "user_id": "99999999",  
            "phone_number": "+256123456786"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
