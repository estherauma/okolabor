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
        self.url = reverse('account:api-notifications', kwargs={'user_id': self.user.id})
    
    def test_create_notification_success(self):
        data = {
            'user_id': self.user.id,
            'title': 'Test Notification',
            'message': 'This is a test notification message.'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UserNotification.objects.filter(user=self.user).count(), 1)
        
    def test_create_notification_invalid_data(self):
        data = {
            'user_id': self.user.id,
            'message': 'This is a test notification message.'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        self.assertIn('title', response.data)

        
    def test_fetch_notifications(self):
        notification = UserNotification.objects.create(
            user=self.user,
            title='Profile Picture Update',
            message='Please update your profile picture.'
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  
        self.assertEqual(response.data[0]['title'], notification.title)  
        self.assertEqual(response.data[0]['message'], notification.message)  
        self.assertEqual(response.data[0]['status'], 'unread')  
        self.assertEqual(response.data[0]['category'], 'general')  
        
        
    def test_mark_notification_as_read(self):
        notification = UserNotification.objects.create(
            user=self.user,
            title='Test Notification',
            message='This is a test notification message.',
            status='unread', 
        )

        data = {
            'notification_id': notification.id,  
            'status': 'read',  
        }

        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notification.refresh_from_db()
        self.assertEqual(notification.status, 'read')
        self.assertEqual(response.data['id'], str(notification.id))
        self.assertEqual(response.data['status'], 'read')
        
    def test_patch_valid_notification_id(self):
        notification = UserNotification.objects.create(
            user=self.user,
            title='Sample Notification',
            message='Sample notification message.',
            status='unread' 
        )
        
        data = {
            'notification_id': notification.id,
            'status': 'read' 
        }
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notification.refresh_from_db()
        self.assertEqual(notification.status, 'read')
        self.assertEqual(response.data['id'], str(notification.id))
        self.assertEqual(response.data['status'], 'read')
        
    def test_patch_invalid_notification_id(self):
        data = {
            'notification_id': 9999,
            'status': 'read'
        }
        
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)




