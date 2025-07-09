from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserPushNotificationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            curp="ZXRC123456NBVCDE21",
            password="password123",
            email='test@fiftyeight.io',
            telephone="1234567890"
        )
        self.url = reverse('account:api-notifications-push-token')
        self.client.force_authenticate(user=self.user)

    def test_update_push_token_success(self):
        data = {'push_notification_token': 'test_token_123'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.push_notification_token, 'test_token_123')

    def test_update_push_token_missing_token(self):
        data = {}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('push_notification_token', response.data['message'])

    def test_update_push_token_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {'push_notification_token': 'test_token_123'}
        response = self.client.post(self.url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])