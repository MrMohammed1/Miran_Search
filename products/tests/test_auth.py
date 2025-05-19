from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
import pytest

@pytest.mark.django_db
class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_obtain_token(self):
        """Test obtaining JWT token with valid credentials."""
        response = self.client.post(
            '/api/token/',
            {'username': 'testuser', 'password': 'testpass'},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_obtain_token_invalid_credentials(self):
        """Test obtaining JWT token with invalid credentials."""
        response = self.client.post(
            '/api/token/',
            {'username': 'testuser', 'password': 'wrongpass'},
            format='json'
        )
        self.assertEqual(response.status_code, 401)

    def test_refresh_token(self):
        """Test refreshing JWT token with valid refresh token."""
        # First, obtain a refresh token
        response = self.client.post(
            '/api/token/',
            {'username': 'testuser', 'password': 'testpass'},
            format='json'
        )
        refresh_token = response.data['refresh']
        # Then, use it to refresh
        response = self.client.post(
            '/api/token/refresh/',
            {'refresh': refresh_token},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)

    def test_protected_endpoint_without_auth(self):
        """Test accessing protected endpoint without authentication."""
        response = self.client.post(
            '/api/products/',
            {'name': 'Banana', 'brand': 'Organic', 'category': 'Fruits', 'calories': 89},
            format='json'
        )
        self.assertEqual(response.status_code, 401)