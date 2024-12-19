from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from account.models import UserNotification
from django.test import TestCase

User = get_user_model()

class UserProfileAviNotificationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            curp="ZXRC123456NBVCDE21",
            password="password123",
            email='test@fiftyeight.io',
            telephone="1234567890"
        )
        self.url = reverse('account:api-notifications-create')
    
    def test_create_notification_success(self):
        data = {'user_id': self.user.id}

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        notification = UserNotification.objects.filter(user=self.user).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.title, 'Actualización de foto de perfil')
        self.assertEqual(notification.message, 'Vaya a su cuenta y configure su foto de perfil.')
        
    def test_user_not_found(self):
        invalid_user_id = 99999  
        response = self.client.post(self.url, {'user_id': invalid_user_id})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

