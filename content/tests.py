from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

class AggregatedContentViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('content:aggregated')

    def test_get_aggregated_content(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
