from unittest.mock import patch
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from account.models import UserDocuments
from django.urls import reverse

class UserDocumentsViewTestCase(APITestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email='test@fiftyeight.io',
            password="password123"
        )

        self.url = reverse('account:api-documents', kwargs={"user_id": self.user.id})

        self.mock_document_data = [
            {
                'path': "/mock/path/1.jpeg",
                'kind': "certificate",
                'description': "Certificate 1 description",
                'cloud_vision_match': True,
                'file_type': "jpeg"
            },
            {
                'path': "/mock/path/2.jpeg",
                'kind': "certificate",
                'description': "Certificate 2 description",
                'cloud_vision_match': False,
                'file_type': "jpeg"
            },
            {
                'path': "/mock/path/3.jpeg",
                'kind': "certificate",
                'description': "Certificate 3 description",
                'cloud_vision_match': False,
                'file_type': None
            }
        ]

        for document_data in self.mock_document_data:
            UserDocuments.objects.create(user=self.user, **document_data)

    def test_get_documents_for_valid_user(self):
        response = self.client.get(self.url, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        documents = response.data
        self.assertEqual(len(documents), 3)
        
        self.assertEqual(documents[0]['path'], self.mock_document_data[0]['path'])
        self.assertEqual(documents[0]['kind'], "certificate")
        self.assertEqual(documents[0]['description'], "Certificate 1 description")
        self.assertEqual(documents[0]['cloud_vision_match'], True)
        self.assertEqual(documents[0]['file_type'], "jpeg")

        self.assertEqual(documents[1]['path'], self.mock_document_data[1]['path'])
        self.assertEqual(documents[1]['kind'], "certificate")
        self.assertEqual(documents[1]['description'], "Certificate 2 description")
        self.assertEqual(documents[1]['cloud_vision_match'], False)
        self.assertEqual(documents[1]['file_type'], "jpeg")

        self.assertEqual(documents[2]['path'], self.mock_document_data[2]['path'])
        self.assertEqual(documents[2]['kind'], "certificate")
        self.assertEqual(documents[2]['description'], "Certificate 3 description")
        self.assertEqual(documents[2]['cloud_vision_match'], False)
        self.assertEqual(documents[2]['file_type'], None)
