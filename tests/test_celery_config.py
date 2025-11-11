"""
Tests for Celery configuration
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class CeleryConfigurationTest(TestCase):
    """Test Celery configuration is properly set up"""

    def test_celery_app_exists(self):
        """Test that Celery app is properly configured"""
        from config import celery_app
        self.assertIsNotNone(celery_app)
        self.assertEqual(celery_app.main, 'config')

    def test_redis_connection_configured(self):
        """Test Redis connection is configured"""
        from config import celery_app
        self.assertTrue(celery_app.conf.broker_url.startswith('redis://'))
        self.assertTrue(celery_app.conf.result_backend.startswith('redis://'))


class UserDeactivationTaskTest(TestCase):
    """Test periodic task for deactivating inactive users"""

    def setUp(self):
        """Set up test users with different last login dates"""
        self.active_user = User.objects.create_user(
            email='active@example.com',
            password='testpass123'
        )
        self.active_user.last_login = timezone.now() - timedelta(days=15)
        self.active_user.save()

        self.inactive_user = User.objects.create_user(
            email='inactive@example.com',
            password='testpass123'
        )
        self.inactive_user.last_login = timezone.now() - timedelta(days=35)
        self.inactive_user.save()

    def test_deactivate_inactive_users_task_exists(self):
        """Test that user deactivation task exists"""
        from config.tasks import deactivate_inactive_users
        result = deactivate_inactive_users.delay()
        self.assertIsNotNone(result)

    def test_deactivate_users_inactive_over_month(self):
        """Test users inactive over a month are deactivated"""
        from config.tasks import deactivate_inactive_users
        deactivate_inactive_users()

        self.active_user.refresh_from_db()
        self.inactive_user.refresh_from_db()

        self.assertTrue(self.active_user.is_active)
        self.assertFalse(self.inactive_user.is_active)