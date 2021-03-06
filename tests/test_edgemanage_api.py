import sys

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, force_authenticate


class EdgemanageAPITestCase(TestCase):

    def setUp(self):
        # Create test user
        self.user = User.objects.create_superuser(
            'testuser', 'testuser@example.com', 'testpassword')
        self.token = Token.objects.create(user=self.user).key
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_api_auth_token(self):

        response = self.client.post('/api-token-auth/', {
            'username': 'testuser',
            'password': 'testpassword'
        })

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check if token is present in JSON body
        self.assertIn('token', response.json())

    def test_edge_query(self):
        response = self.client.get('/api/edgemanage/list', {
            'dnet': settings.EDGEMANAGE_DNET
        })

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

    def test_dnet_query(self):
        response = self.client.get('/api/edgemanage/dnet')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

    def test_edge_conf(self):
        response = self.client.put('/api/edgemanage/config', {
            'dnet': settings.EDGEMANAGE_DNET,
            'edge': settings.EDGEMANAGE_TEST_EDGE,
            'mode': 'unavailable',
            'comment': 'test rotate',
            'comment_user': 'circleci'
        })
        self.assertEqual(response.status_code, 201)
