"""
Password reset tests (Djoser)
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class PasswordResetTest(TestCase):
    """Test password reset functionality"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="oldpassword123",
            first_name="Test",
            last_name="User",
        )

    def test_request_password_reset(self):
        """Test requesting password reset"""
        url = "/api/auth/users/reset_password/"
        data = {"email": "test@example.com"}

        response = self.client.post(url, data)

        # Should return 204 even if email doesn't exist (security)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_request_password_reset_nonexistent_email(self):
        """Test requesting password reset for nonexistent email"""
        url = "/api/auth/users/reset_password/"
        data = {"email": "nonexistent@example.com"}

        response = self.client.post(url, data)

        # Should return 204 (don't reveal if email exists)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_request_password_reset_invalid_email(self):
        """Test requesting password reset with invalid email format"""
        url = "/api/auth/users/reset_password/"
        data = {"email": "invalid-email"}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
