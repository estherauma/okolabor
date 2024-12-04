from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from account.models import UserPreference, UserWorkExperience

User = get_user_model()

class ResetAccountProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='Testing321123',
            first_name='Test',
            last_name='User'
        )
       
        self.url = reverse('account:reset-profile', kwargs={'user_id': self.user.id})

    def test_account_reset_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'message': 'Profile reset successfully'})

        self.assertFalse(UserPreference.objects.filter(user=self.user).exists())
        self.assertFalse(UserWorkExperience.objects.filter(user=self.user).exists())
