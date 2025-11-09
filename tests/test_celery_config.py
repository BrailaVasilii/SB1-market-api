"""
Tests for Celery configuration and tasks
Following TDD principles - Red phase
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch

from materials.models import Course

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
        # Test broker and result backend are configured
        self.assertTrue(celery_app.conf.broker_url.startswith('redis://'))
        self.assertTrue(celery_app.conf.result_backend.startswith('redis://'))


class EmailNotificationTaskTest(TestCase):
    """Test email notification tasks for course updates"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description'
        )

    @patch('config.tasks.send_mail')
    def test_send_course_update_notification_task_exists(self, mock_send_mail):
        """Test that course update notification task exists and works"""
        from config.tasks import send_course_update_notification

        # Task should be callable
        result = send_course_update_notification.delay(self.course.id)
        self.assertIsNotNone(result)

    @patch('config.tasks.send_mail')
    def test_course_update_notification_sends_to_subscribers(self, mock_send_mail):
        """Test notification is sent to all course subscribers"""
        from config.tasks import send_course_update_notification

        send_course_update_notification(self.course.id)

        # Verify email was sent
        mock_send_mail.assert_called_once()
        args = mock_send_mail.call_args[1]
        self.assertIn(self.user.email, args['recipient_list'])
        self.assertIn(self.course.title, args['subject'])


class UserDeactivationTaskTest(TestCase):
    """Test periodic task for deactivating inactive users"""

    def setUp(self):
        """Set up test users with different last login dates"""
        # Active user (logged in recently)
        self.active_user = User.objects.create_user(
            email='active@example.com',
            password='testpass123'
        )
        self.active_user.last_login = timezone.now() - timedelta(days=15)
        self.active_user.save()

        # Inactive user (not logged in for over a month)
        self.inactive_user = User.objects.create_user(
            email='inactive@example.com',
            password='testpass123'
        )
        self.inactive_user.last_login = timezone.now() - timedelta(days=35)
        self.inactive_user.save()

    def test_deactivate_inactive_users_task_exists(self):
        """Test that user deactivation task exists"""
        from config.tasks import deactivate_inactive_users

        # Task should be callable
        result = deactivate_inactive_users.delay()
        self.assertIsNotNone(result)

    def test_deactivate_users_inactive_over_month(self):
        """Test users inactive over a month are deactivated"""
        from config.tasks import deactivate_inactive_users

        # Run the task
        deactivate_inactive_users()

        # Refresh from database
        self.active_user.refresh_from_db()
        self.inactive_user.refresh_from_db()

        # Active user should remain active
        self.assertTrue(self.active_user.is_active)

        # Inactive user should be deactivated
        self.assertFalse(self.inactive_user.is_active)


class CourseUpdateThrottlingTest(TestCase):
    """Test course update throttling feature"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description'
        )

    def test_course_update_within_four_hours_no_notification(self):
        """Test no notification sent if course updated within 4 hours"""
        from config.tasks import send_course_update_notification_with_throttling

        # Update course recently
        self.course.updated_at = timezone.now() - timedelta(hours=2)
        self.course.save()

        with patch('config.tasks.send_course_update_notification') as mock_task:
            send_course_update_notification_with_throttling(self.course.id)
            mock_task.delay.assert_not_called()

    def test_course_update_after_four_hours_sends_notification(self):
        """Test notification sent if course not updated for over 4 hours"""
        from config.tasks import send_course_update_notification_with_throttling

        # Update course more than 4 hours ago
        self.course.updated_at = timezone.now() - timedelta(hours=5)
        self.course.save()

        # Mock the actual task instead of module import
        with patch('config.tasks.send_course_update_notification.delay') as mock_task:
            result = send_course_update_notification_with_throttling(self.course.id)
            mock_task.assert_called_once_with(self.course.id)
            self.assertEqual(result['status'], 'notification_sent')


class CeleryBeatScheduleTest(TestCase):
    """Test Celery Beat periodic task scheduling"""

    def test_periodic_task_schedule_configured(self):
        """Test that periodic tasks are properly scheduled"""
        from config import celery_app

        # Check that beat schedule is configured
        self.assertIsNotNone(celery_app.conf.beat_schedule)

        # Check specific task is scheduled
        schedule = celery_app.conf.beat_schedule
        self.assertIn('deactivate-inactive-users', schedule)

        # Verify task runs daily
        task_config = schedule['deactivate-inactive-users']
        self.assertEqual(
            task_config['task'], 'config.tasks.deactivate_inactive_users')
