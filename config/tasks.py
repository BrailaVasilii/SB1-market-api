"""
Celery tasks for LMS platform
Following TDD principles and Django best practices
"""
from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

from materials.models import Course

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_course_update_notification(self, course_id: int) -> dict:
    """
    Send email notifications to all subscribers of a course

    Args:
        course_id: ID of the updated course

    Returns:
        dict: Task execution result with statistics
    """
    try:
        # Get course
        course = Course.objects.get(id=course_id)

        # For SB1 Market API - no subscription model needed
        # This function is disabled as subscriptions are not part of the market API
        logger.info(f"Course update notification skipped for {course.title} - not implemented for market API")
        return {
            'status': 'success',
            'course_id': course_id,
            'notifications_sent': 0,
            'message': 'Subscription notifications not implemented for market API'
        }

        # Prepare email content (kept for reference but not used)
        subject = f"Course Update: {course.title}"
        message = f"""
Hello!

The course "{course.title}" has been updated with new content.

Course Description: {course.description}

Log in to your LMS platform to check out the latest updates!

Best regards,
LMS Platform Team
        """

        # No subscribers for market API
        recipient_list = []

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )

        logger.info(
            f"Course update notifications sent for {course.title} "
            f"to {len(recipient_list)} users")

        return {
            'status': 'success',
            'course_id': course_id,
            'notifications_sent': len(recipient_list),
            'recipients': recipient_list
        }

    except Course.DoesNotExist:
        logger.error(f"Course with ID {course_id} not found")
        return {
            'status': 'error',
            'course_id': course_id,
            'error': 'Course not found'
        }

    except Exception as exc:
        logger.error(f"Error sending course update notifications: {str(exc)}")
        # Retry the task
        raise self.retry(exc=exc, countdown=60)


@shared_task
def deactivate_inactive_users() -> dict:
    """
    Deactivate users who haven't logged in for more than a month
    Periodic task that runs daily

    Returns:
        dict: Task execution result with statistics
    """
    try:
        # Calculate cutoff date (1 month ago)
        cutoff_date = timezone.now() - timedelta(days=30)

        # Find users who haven't logged in for over a month and are still active
        inactive_users = User.objects.filter(
            last_login__lt=cutoff_date,
            is_active=True
        )

        # Count for logging
        user_count = inactive_users.count()

        if user_count == 0:
            logger.info("No inactive users found to deactivate")
            return {
                'status': 'success',
                'users_deactivated': 0,
                'message': 'No inactive users found'
            }

        # Get user emails for logging
        user_emails = list(inactive_users.values_list('email', flat=True))

        # Deactivate users
        inactive_users.update(is_active=False)

        logger.info(f"Deactivated {user_count} inactive users: {user_emails}")

        return {
            'status': 'success',
            'users_deactivated': user_count,
            'deactivated_users': user_emails,
            'cutoff_date': cutoff_date.isoformat()
        }

    except Exception as exc:
        logger.error(f"Error deactivating inactive users: {str(exc)}")
        return {
            'status': 'error',
            'error': str(exc)
        }


@shared_task
def send_course_update_notification_with_throttling(course_id: int) -> dict:
    """
    Send course update notification with throttling
    Only sends notification if course wasn't updated within last 4 hours

    Args:
        course_id: ID of the updated course

    Returns:
        dict: Task execution result
    """
    try:
        course = Course.objects.get(id=course_id)

        # Check if course was updated within last 4 hours
        four_hours_ago = timezone.now() - timedelta(hours=4)

        if course.updated_at > four_hours_ago:
            logger.info(
                f"Course {course.title} was updated recently, skipping notification")
            return {
                'status': 'skipped',
                'course_id': course_id,
                'reason': 'Course updated within last 4 hours',
                'last_update': course.updated_at.isoformat()
            }

        # Course wasn't updated recently, send notification
        send_course_update_notification.delay(course_id)

        return {
            'status': 'notification_sent',
            'course_id': course_id,
            'last_update': course.updated_at.isoformat()
        }

    except Course.DoesNotExist:
        logger.error(f"Course with ID {course_id} not found")
        return {
            'status': 'error',
            'course_id': course_id,
            'error': 'Course not found'
        }

    except Exception as exc:
        logger.error(f"Error in throttled notification: {str(exc)}")
        return {
            'status': 'error',
            'course_id': course_id,
            'error': str(exc)
        }
