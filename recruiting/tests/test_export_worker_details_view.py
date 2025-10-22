from unittest.mock import patch, MagicMock
from django.urls import reverse
from io import BytesIO
import pandas as pd
from rest_framework import status
from account.models import User, UserPreference
from content.models import AggregatedContent
from django.test import TestCase

class ExportWorkerDetailsTest(TestCase):
    @patch('content.models.AggregatedContent.objects.latest')
    @patch('account.models.User.objects.filter')
    @patch('account.models.UserPreference.objects.filter')
    def test_export_worker_details(self, mock_user_preferences, mock_user_filter, mock_latest_content):
        mock_aggregated_content = MagicMock()
        mock_aggregated_content.get.return_value = {
            'en': {
                'workPreferenceStepOne': {'form_questions': [{'key': 'question1', 'label': 'Question 1'}]},
                'workPreferenceStepTwo': {'form_questions': [{'key': 'question2', 'label': 'Question 2'}]},
                'profileStepOne': {'form_questions': [{'key': 'question3', 'label': 'Question 3'}]},
                'profileStepTwo': {'form_questions': [{'key': 'question4', 'label': 'Question 4'}], 'pageTitle': 'English Proficiency'},
            }
        }
        mock_latest_content.return_value = mock_aggregated_content

        mock_user = MagicMock(spec=User)
        mock_user.username = "worker1"
        mock_user_filter.return_value = [mock_user]

        mock_user_preference = MagicMock(spec=UserPreference)
        mock_user_preference.key = 'question1'
        mock_user_preference.value = 'Answer 1'
        mock_user_preferences.return_value = [mock_user_preference]

        url = reverse('recruiting_web:export-workers')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertIn('attachment; filename="workers.xlsx"', response['Content-Disposition'])

        excel_file = BytesIO(response.content)
        df = pd.read_excel(excel_file)

        self.assertIn('QUESTION1', df.columns)
        self.assertEqual(df.iloc[0]['QUESTION1'], 'Answer 1')