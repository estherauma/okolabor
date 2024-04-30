import unittest
from unittest.mock import patch
from rest_framework.test import APIRequestFactory
from account.views.api import IndexView

class APIRootTestCase(unittest.TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_get(self):
        # Arrange
        view = IndexView.as_view()
        request = self.factory.get('/api/endpoint')

        # Act
        response = view(request)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'message': 'Hello, World!'})

if __name__ == '__main__':
    unittest.main()
