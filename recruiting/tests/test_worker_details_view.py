from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from account.models import UserPreference

User = get_user_model()

class WorkerDetailsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.worker = User.objects.create_user(
            curp="TESTCURP123456789",
            email="testworker@example.com",
            password="testpassword"
        )

        UserPreference.objects.create(user=self.worker, key="workplaces", value="Office1,Office2")
        UserPreference.objects.create(user=self.worker, key="Prefered_Employes", value="Emp1,Emp2")
        UserPreference.objects.create(user=self.worker, key="language", value="English")

    def test_worker_details_view_success(self):
        """Test WorkerDetailsView with a valid worker ID"""
        url = reverse("recruiting_web:worker_detail", kwargs={"pk": self.worker.id})  # ✅ Use curp

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiting/workers/detail.html")
        self.assertEqual(response.context["worker"], self.worker)

    def test_worker_details_view_worker_not_found(self):
        """Test WorkerDetailsView with an invalid worker ID"""
        invalid_pk = "INVALIDCURP123456"
        url = reverse("recruiting_web:worker_detail", kwargs={"pk": invalid_pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
