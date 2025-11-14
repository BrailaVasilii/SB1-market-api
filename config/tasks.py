"""
Celery tasks for SB1 Market API
"""

import logging
from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()
logger = logging.getLogger(__name__)


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
        inactive_users = User.objects.filter(last_login__lt=cutoff_date, is_active=True)

        # Count for logging
        user_count = inactive_users.count()

        if user_count == 0:
            logger.info("No inactive users found to deactivate")
            return {
                "status": "success",
                "users_deactivated": 0,
                "message": "No inactive users found",
            }

        # Get user emails for logging
        user_emails = list(inactive_users.values_list("email", flat=True))

        # Deactivate users
        inactive_users.update(is_active=False)

        logger.info(f"Deactivated {user_count} inactive users: {user_emails}")

        return {
            "status": "success",
            "users_deactivated": user_count,
            "deactivated_users": user_emails,
            "cutoff_date": cutoff_date.isoformat(),
        }

    except Exception as exc:
        logger.error(f"Error deactivating inactive users: {str(exc)}")
        return {"status": "error", "error": str(exc)}
