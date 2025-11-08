"""
Celery configuration for the LMS project
Following Django best practices and modular structure
"""
import os
from celery import Celery
from decouple import config

# Set default Django settings module for 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create Celery app instance
app = Celery('config')

# Configure Celery using Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed Django apps
app.autodiscover_tasks()

# Redis configuration from environment variables
app.conf.update(
    broker_url=config('REDIS_URL', default='redis://localhost:6379/0'),
    result_backend=config('REDIS_URL', default='redis://localhost:6379/0'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    # Task routing
    task_routes={
        'config.tasks.send_course_update_notification': {'queue': 'email'},
        'config.tasks.deactivate_inactive_users': {'queue': 'maintenance'},
    },
    # Beat scheduler configuration
    beat_scheduler='django_celery_beat.schedulers:DatabaseScheduler',
    beat_schedule={
        'deactivate-inactive-users': {
            'task': 'config.tasks.deactivate_inactive_users',
            'schedule': 86400.0,  # Run daily (24 hours in seconds)
            'options': {'queue': 'maintenance'}
        },
    },
)


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery configuration"""
    print(f'Request: {self.request!r}')
    return 'Debug task completed successfully'
