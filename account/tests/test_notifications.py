from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from account.models import UserNotification
from django.contrib.auth import get_user_model


User = get_user_model()
class UserNotificationViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            email="test@example.com",
            curp="CURP12345678",
            first_name="Test",
            last_name="User",
            telephone="1234567890",
        )
        self.notification = UserNotification.objects.create(
            user=self.user, title="Test Notification", message="This is a test."
        )
        self.url = reverse('account:api-report-problem', kwargs={'user_id': self.user.id})
        
    def test_retrieve_user_notifications(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Test Notification")
        self.assertEqual(response.data[0]['message'], "This is a test.")
        
    def test_create_user_notification(self):
        notification_data = {
            "title": "New Test Notification",
            "message": "This is a new test notification"
        }
        response = self.client.post(self.url, notification_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], "New Test Notification")
        self.assertEqual(response.data['message'], "This is a new test notification")
        self.assertEqual(UserNotification.objects.count(), 2)

