from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import get_user_model

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

    
    def test_generate_otp_missing_fields(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 400)
        self.assertIn('user_id', response.data)
        self.assertIn('phone_number', response.data)
        
    def test_generate_otp_invalid_user_id(self):
        response = self.client.post(self.url, {'user_id': 'invalid_id', 'phone_number': '+256123456781'})
        self.assertEqual(response.status_code, 400)
       