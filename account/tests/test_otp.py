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
        
    def test_generate_otp_empty_request(self):
        data = {}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("user_id", response.data)
        self.assertIn("phone_number", response.data)
        
    @patch('account.serializers.OTPGenerateSerializer.start_otp_process')
    def test_generate_otp_user_update(self, mock_start_otp_process):
        mock_start_otp_process.return_value = "pending"
        data = {
            "user_id": str(self.user.id),
            "phone_number": "+256123456784"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.telephone, "+256123456784")
        
class VerifyOTPTests(APITestCase):
    def setUp(self):
            self.user = User.objects.create_user(
            curp='CURR123456HRDACV55',
            email='test@example.com',
            password='Testing321123',
            first_name='Test',
            last_name='User',
            telephone='+256123456781'
        )
            self.user_id = str(self.user.id)
            self.client.force_authenticate(user=self.user)
            self.url = reverse('account:otp-verify')
            
    @patch('account.serializers.OTPVerifySerializer.verify_otp')
    def test_otp_verification_success(self, mock_verify_otp):
        mock_verify_otp.return_value = 'approved'
        data = {
            "user_id": str(self.user.id),
            "phone_number": "+256123456780",
            "otp_code": "3456"
        }
        
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "approved")
        
    @patch('account.serializers.OTPVerifySerializer.verify_otp')
    def test_otp_verification_error(self, mock_verify_otp):
        mock_verify_otp.return_value = {"error": "Invalid OTP"}
        data = {
            "user_id": str(self.user.id),
            "phone_number": "+256123456789",
            "otp_code": "1234"
        }
        
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["status"], "error")
        self.assertEqual(response.data["error"], "Invalid OTP")
        
    def test_otp_verification_validation_error(self):
        data = {
            "user_id": "",
            "phone_number": "+256123456789",
            "otp_code": "1234"
        }
        
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("user_id", response.data)
