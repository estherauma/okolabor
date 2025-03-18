from django.test import TestCase, Client
from django.urls import reverse
from account.models import User
from django.contrib.auth.models import Group

class WorkerListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = '/workers/'  # Ensure this matches your URL name
        self.worker_group = Group.objects.create(name='worker')

        # Provide unique `curp` values for each user
        self.worker1 = User.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            curp='unique_curp_1'
        )
        self.worker1.groups.add(self.worker_group)

        self.worker2 = User.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane.smith@example.com',
            curp='unique_curp_2'
        )
        self.worker2.groups.add(self.worker_group)

    def test_worker_list_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('workers', response.context)
        self.assertIn('form', response.context)
        self.assertIn('filter_form', response.context)
        self.assertIn('search_query', response.context)
        self.assertIn('paginator', response.context)

    def test_worker_search(self):
        response = self.client.get(self.url, {'search': 'John'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.worker1, response.context['workers'])
        self.assertNotIn(self.worker2, response.context['workers'])

    def test_ajax_request(self):
        response = self.client.get(self.url, {'search': 'John'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertIn('workers', data)
        self.assertEqual(len(data['workers']), 1)
        self.assertEqual(data['workers'][0]['firstname'], 'John')
