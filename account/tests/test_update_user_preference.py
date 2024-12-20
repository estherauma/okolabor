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
        
    def test_partial_update_preferences(self):
        data = {
            "preferences": [
                {"key": "theme", "value": "dark", "kind": "ui"}  
            ]
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pref1.refresh_from_db()
        self.assertEqual(self.pref1.value, "dark")
        self.pref2.refresh_from_db()
        self.assertEqual(self.pref2.value, "English")
        
    def test_invalid_payload(self):
        data = {
            "preferences": "invalid data type"  
        }
        with self.assertRaises(TypeError) as context:
            self.client.post(self.url, data, format="json")
        self.assertIn("string indices must be integers", str(context.exception))
        
    def test_resolve_duplicate_keys_by_overwriting(self):
        data = {
            "preferences": [
                {"key": "theme", "value": "dark", "kind": "ui"},
                {"key": "theme", "value": "light", "kind": "ui"}
            ]
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        preferences = UserPreference.objects.filter(user=self.user, key="theme")
        self.assertEqual(preferences.count(), 1)  
        self.assertEqual(preferences.first().value, "light")

    def test_invalid_user_id(self):
        invalid_url = reverse('account:update-user-preferences', kwargs={"user_id": 999})
        data = {
            "preferences": [
                {"key": "theme", "value": "dark", "kind": "ui"}
            ]
        }
        response = self.client.post(invalid_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_update_user_model_fields(self):
        data = {
            "preferences": [
                {"key": "firstName", "value": "UpdatedName", "kind": "profile"},
                {"key": "gender", "value": "Male", "kind": "profile"}
            ]
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "UpdatedName")
        self.assertEqual(self.user.gender, "Male")
        
    def test_get_all_preferences(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        preferences = response.data
        self.assertEqual(len(preferences), 2)
        self.assertEqual(preferences[0]['key'], 'theme')
        self.assertEqual(preferences[1]['key'], 'language')
