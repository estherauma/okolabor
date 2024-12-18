from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from account.models import UserPreference
from django.contrib.auth import get_user_model

class UserPreferencesUpdateViewTestCase(APITestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            curp="ABCD123456NBFVDX12",
            email='test@fiftyeight.io',
            password="password123"
        )
        
        self.url = reverse('account:update-user-preferences', kwargs={"user_id": self.user.id})
        
        self.pref1 = UserPreference.objects.create(
            user=self.user, key="theme", value="light", kind="ui"
        )
        self.pref2 = UserPreference.objects.create(
            user=self.user, key="language", value="English", kind="setting"
        )

    def test_create_new_preferences(self):
        data = {
            "preferences": [
                {"key": "theme", "value": "dark", "kind": "ui"},
                {"key": "language", "value": "Spanish", "kind": "setting"}
            ]
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['value'], "dark")
        self.assertEqual(response.data[1]['value'], "Spanish")
        
    def test_update_existing_preferences(self):
        data = {
            "preferences": [
                {"key": "theme", "value": "dark", "kind": "ui"}, 
                {"key": "language", "value": "Spanish", "kind": "setting"},
            ]
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.pref1.refresh_from_db()
        self.pref2.refresh_from_db()

        self.assertEqual(self.pref1.value, "dark")
        self.assertEqual(self.pref2.value, "Spanish")
        
    def test_ignore_empty_or_none_values(self):
        
        data = {
            "preferences": [
                {"key": "theme", "value": None, "kind": "ui"},  
                {"key": "language", "value": "", "kind": "setting"}, 
                {"key": "notifications", "value": "enabled", "kind": "setting"} 
            ]
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        preferences = UserPreference.objects.filter(user=self.user)
        self.assertEqual(preferences.count(), 3) 

        self.assertTrue(
            preferences.filter(key="notifications", value="enabled", kind="setting").exists()
        )
