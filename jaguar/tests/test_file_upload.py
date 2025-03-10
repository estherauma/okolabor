from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
import tempfile
import os
from django.contrib.auth import get_user_model

User = get_user_model()
class UploadFileViewTestCase(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            curp = "TEST123456BVCXSD12",
            password='Testing321123',
            first_name='Test',
            last_name='User'
            )
        self.url = reverse('file-upload')  
        
    def authenticate(self):
        self.client.login(email="test@example.com", password="Testing321123")
        
    def create_test_file(self, entity_type):
        file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
        file.write(b'This is a test file.')
        file.close()
        return file.name
    
    def test_upload_file_success(self):
        self.authenticate()
        file_path = self.create_test_file(entity_type='contract')
        
        with open(file_path, 'rb') as file:
            data = {
                'entity_type': 'contract',
                'file_content': file,
                'description': 'Test contract file'
            }
            response = self.client.post(self.url, data, format='multipart')
            os.remove(file_path)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('document_id', response.data)
        self.assertIn('file_location', response.data)
        self.assertIn('file_type', response.data)
        self.assertTrue(os.path.exists(response.data['file_location']))
        
    def test_upload_invalid_entity_type(self):
        self.authenticate()
        file_path = self.create_test_file(entity_type='unknown_entity')
        
        with open(file_path, 'rb') as file:
            data = {
                'entity_type': 'unknown_entity',
                'file_content': file
            }
            response = self.client.post(self.url, data, format='multipart')
            os.remove(file_path) 
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid entity type')
        
    def test_upload_no_authentication(self):
        file_path = self.create_test_file(entity_type='contract')
        
        with open(file_path, 'rb') as file:
            data = {
                'entity_type': 'contract',
                'file_content': file
            }
            response = self.client.post(self.url, data, format='multipart')
            os.remove(file_path) 

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('detail', response.data) 
        self.assertEqual(str(response.data['detail']), 'Authentication credentials were not provided.')

    def test_upload_invalid_file(self):
        self.authenticate()
        data = {
            'entity_type': 'contract',
            'description': 'Missing file'
        }
        response = self.client.post(self.url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file_content', response.data)
        self.assertEqual(response.data['file_content'][0], 'No file was submitted.')
