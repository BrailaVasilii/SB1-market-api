"""
Authentication tests (JWT)
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class JWTAuthenticationTest(TestCase):
    """Test JWT authentication"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_obtain_jwt_token_success(self):
        """Test obtaining JWT token with valid credentials"""
        url = reverse("users:token_obtain_pair")
        data = {"email": "test@example.com", "password": "testpass123"}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_obtain_jwt_token_invalid_password(self):
        """Test obtaining JWT token with invalid password"""
        url = reverse("users:token_obtain_pair")
        data = {"email": "test@example.com", "password": "wrongpassword"}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_obtain_jwt_token_nonexistent_user(self):
        """Test obtaining JWT token with nonexistent user"""
        url = reverse("users:token_obtain_pair")
        data = {"email": "nonexistent@example.com", "password": "testpass123"}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_jwt_token_success(self):
        """Test refreshing JWT token"""
        # First get tokens
        token_url = reverse("users:token_obtain_pair")
        token_data = {"email": "test@example.com", "password": "testpass123"}
        token_response = self.client.post(token_url, token_data)
        refresh_token = token_response.data["refresh"]

        # Now refresh
        refresh_url = reverse("users:token_refresh")
        refresh_data = {"refresh": refresh_token}

        response = self.client.post(refresh_url, refresh_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_refresh_jwt_token_invalid(self):
        """Test refreshing JWT token with invalid token"""
        url = reverse("users:token_refresh")
        data = {"refresh": "invalid_token"}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_protected_endpoint_with_token(self):
        """Test accessing protected endpoint with valid token"""
        # Get token
        token_url = reverse("users:token_obtain_pair")
        token_data = {"email": "test@example.com", "password": "testpass123"}
        token_response = self.client.post(token_url, token_data)
        access_token = token_response.data["access"]

        # Access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        url = reverse("materials:advertisement-list")
        data = {"title": "Test Product", "price": 1000, "description": "Test"}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_access_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        url = reverse("materials:advertisement-list")
        data = {"title": "Test Product", "price": 1000, "description": "Test"}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
