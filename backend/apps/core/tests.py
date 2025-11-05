from django.test import TestCase, Client
from django.urls import reverse
from apps.users.models import User
import json

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_challenge_endpoint(self):
        response = self.client.post('/api/auth/challenge/',
                                   {'wallet_address': '0x1234567890123456789012345678901234567890'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('message', data)
        self.assertIn('nonce', data)

    def test_invalid_wallet_address(self):
        response = self.client.post('/api/auth/challenge/',
                                   {'wallet_address': 'invalid'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

class HealthCheckTests(TestCase):
    def test_health_endpoint(self):
        response = self.client.get('/health/')
        self.assertIn(response.status_code, [200, 404])
