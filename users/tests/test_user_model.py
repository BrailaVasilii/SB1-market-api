from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase


class UserModelTest(TestCase):
    """Test cases for Custom User model following TDD approach"""

    def test_create_user_with_email_successful(self):
        """Test creating a user with email is successful"""
        email = "test@example.com"
        password = "testpass123"
        phone = "+373123456789"
        city = "Chisinau"

        user = get_user_model().objects.create_user(
            email=email, password=password, phone=phone, city=city
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertEqual(user.phone, phone)
        self.assertEqual(user.city, city)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = "test@EXAMPLE.COM"
        user = get_user_model().objects.create_user(email, "test123")

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "test123")

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser("test@example.com", "test123")

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_user_str_representation(self):
        """Test the string representation of user"""
        user = get_user_model().objects.create_user(
            email="test@example.com", password="testpass123"
        )

        self.assertEqual(str(user), user.email)
