import unittest
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.test.testcases import TestCase
User = get_user_model()


class RegistrationAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_registration_success(self):
        url = reverse('account:api-register')
        data = {
            'email': 'test@example.com',
            'curp': 'HEGJ820506HBCRRN09',
            'password': 'adminwert1A',
            'password_repeat': 'adminwert1A'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().email, 'test@example.com')
        self.assertEqual(User.objects.first().curp, 'HEGJ820506HBCRRN09')
        self.assertFalse(User.objects.first().is_active)
        self.assertFalse(User.objects.first().is_verified)

    def test_registration_invalid_email(self):
        url = reverse('account:api-register')
        data = {
            'email': 'invalid_email',
            'curp': 'HEGJ820506HBCRRN09',
            'password': 'testpassword',
            'password_repeat': 'testpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.data['email'][0], 'Enter a valid email address.')

    def test_registration_curp(self):
        url = reverse('account:api-register')
        data = {
            'email': 'invalid_email',
            'curp': 'HEGJ820506HBCRRN',
            'password': 'testpassword',
            'password_repeat': 'testpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.data['curp'][0], 'CURP cannot be less than 18 characters long')

    def test_registration_invalid_password(self):
        url = reverse('account:api-register')
        data = {
            'email': 'invalid_email',
            'curp': 'HEGJ820506HBCRRN09',
            'password': 'testpassword',
            'password_repeat': 'testpas'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.data['password'][0], 'Passwords do not match')

class RegistrationTestCase(TestCase):
    def setUp(self):
        self.client= APIClient()
    def test_registration_template(self):
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ltr/register.html')

    def test_registration_success(self):
        response =self.client.post('/register',{
           'email': 'test@example.com',
            'curp': 'HEGJ820506HBCRRN09',
            'password': 'adminwert1A',
            'password_repeat': 'adminwert1A'
        })
        self.assertEquals(response.status_code, 200)
        
        

    def test_registration_invalid_credentials(self):
        response =self.client.post('/register',{
           'email': 'test@example.com',
            'curp': 'HEGJ820506HBCRRN09',
            'password': 'adminwert1A',
            'password_repeat': 'adminwert1A'
        })
        self.assertEquals(response.status_code, 200)
        
     

if __name__ == '__main__':
    unittest.main()
