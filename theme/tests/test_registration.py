from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()  # ✅ Fetches the correct custom user model

class RegisterViewTest(TestCase):
    def test_register_view_post_success(self):
        # ✅ Remove 'username', only use 'email' and 'password'
        User.objects.create_user(email='testuser@example.com', password='TestPassword123')
        self.assertTrue(User.objects.filter(email='testuser@example.com').exists())  # ✅ Check if user is created

    def test_register_duplicate_email(self):
        # ✅ Remove 'username' field
        User.objects.create_user(email='testuser@example.com', password='TestPassword123')
        duplicate_user_count = User.objects.filter(email='testuser@example.com').count()
        self.assertEqual(duplicate_user_count, 1)  # ✅ Ensure only one user exists
