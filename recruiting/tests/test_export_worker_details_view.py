from unittest.mock import patch, MagicMock
from django.urls import reverse
from io import BytesIO
import pandas as pd
from rest_framework import status
from account.models import User, UserPreference
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


class ExportWorkerDetailsTest(TestCase):
    @patch('recruiting.views.workers.AggregatedContentSerializer')
    @patch('recruiting.views.workers.AggregatedContent.objects.latest')
    def test_export_worker_details(self, mock_latest_content, mock_serializer):
        User = get_user_model()
        
        user = User.objects.create_user(email='admin@okolabor.com', password='testpass')
        
        worker_group, _ = Group.objects.get_or_create(name='worker')
        
        worker = User.objects.create_user(email='worker@okolabor.com', password='testpass')
        worker.groups.add(worker_group)
        
        UserPreference.objects.create(user=worker, key='question1', value='Answer 1')

        mock_content = MagicMock()
        mock_latest_content.return_value = mock_content

        mock_serializer_instance = MagicMock()
        mock_serializer_instance.data = {
            'content': {
                'en': {
                    'workPreferenceStepOne': {'form_questions': [{'key': 'question1', 'label': 'Question 1'}]},
                    'workPreferenceStepTwo': {'form_questions': []},
                    'profileStepOne': {'form_questions': []},
                    'profileStepTwo': {'form_questions': []},
                }
            }
        }
        mock_serializer.return_value = mock_serializer_instance

        self.client.login(email='admin@okolabor.com', password='testpass')

        url = reverse('recruiting_web:export-workers')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertIn('attachment; filename="workers.xlsx"', response['Content-Disposition'])

        excel_file = BytesIO(response.content)
        df = pd.read_excel(excel_file, sheet_name='Workers')

        self.assertIn('QUESTION 1', df.columns)
        self.assertEqual(df.iloc[0]['QUESTION 1'], 'Answer 1')
