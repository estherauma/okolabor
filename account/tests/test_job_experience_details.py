from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from account.models import User, UserJobExperience, UserJobExperienceDetails

class UserJobExperienceDetailsViewTest(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            curp="CURP123456ABCDEF76",
            email="testuser@example.com",
            password="testpass123",
            telephone="1234567890"
        )
        
        self.job_experience = UserJobExperience.objects.create(
            user=self.user,
            job_type="Full Time",
            type_details="Remote"
        )
        
        self.job_experience_detail = UserJobExperienceDetails.objects.create(
            job_experience=self.job_experience,
            created_by=self.user.id,
            updated_by=self.user.id,
            kind="Skill",
            value="Python"
        )
        
        self.client = APIClient()
        self.url = reverse('account:api-job-experience-details', kwargs={'user_id': self.user.id})
        
    def test_post_job_experience_details_success(self):
       
        data = {
            "job_experience_id": self.job_experience.id,
            "details": [
                {"kind": "responsibilities", "value": "Django development"},
                {"kind": "license", "value": "Driver's License"}
            ]
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['created']), 2)
        self.assertEqual(response.data['created'][0]['value'], "Django development")
        self.assertEqual(response.data['created'][1]['value'], "Driver's License")
        
    def test_post_job_experience_details_with_invalid_data(self):
        data = {
            "job_experience_id": self.job_experience.id,
            "details": [
                {"kind": "responsibilities", "value": "Django development"},
                {"kind": "license", "value": None},  
                {"kind": "certification", "value": ""}
            ]
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['created']), 1)  
        self.assertEqual(response.data['created'][0]['value'], "Django development")
        
    def test_post_job_experience_details_with_missing_details(self):
      
        data = {
            "job_experience_id": self.job_experience.id
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['created']), 0) 
        
    def test_post_job_experience_details_with_empty_details(self):
        data = {
            "job_experience_id": self.job_experience.id,
            "details": []
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['created']), 0) 
        
    def test_post_job_experience_details_invalid_job_experience_id(self):
        
        data = {
            "job_experience_id": 9999,  
            "details": [{"kind": "skill", "value": "JavaScript"}]
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_post_job_experience_details_user_not_found(self):
        
        url = reverse('account:api-job-experience-details', kwargs={'user_id': 9999})
        data = {
            "job_experience_id": self.job_experience.id,
            "details": [{"kind": "skill", "value": "React"}]
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_post_job_experience_details_no_job_experience_id(self):
        
        data = {
            "details": [{"kind": "responsibilities", "value": "Leadership"}]
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_patch_job_experience_details_success(self):
        
        patch_data = {
            "job_experience_details_id": self.job_experience_detail.id,
            "value": "Updated Value"
        }

        response = self.client.patch(self.url, patch_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job_experience_detail.refresh_from_db()
        self.assertEqual(self.job_experience_detail.value, "Updated Value")
        
    def test_patch_job_experience_details_invalid_id(self):
        
        patch_data = {
            "job_experience_details_id": 9999, 
            "value": "Invalid Update"
        }

        response = self.client.patch(self.url, patch_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_patch_job_experience_details_missing_id(self):
        
        patch_data = {
            "value": "Missing ID Update"
        }

        response = self.client.patch(self.url, patch_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


