"""
Django management command to start Celery Beat scheduler
Following Django best practices for management commands
"""

import subprocess
import sys

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Start Celery Beat scheduler for periodic tasks"""

    help = "Start Celery Beat scheduler for periodic task execution"

    def add_arguments(self, parser):
        """Add command arguments"""
        parser.add_argument(
            "--loglevel", default="info", help="Logging level (default: info)"
        )
        parser.add_argument(
            "--scheduler",
            default="django_celery_beat.schedulers:DatabaseScheduler",
            help="Scheduler class "
            "(default: django_celery_beat.schedulers:DatabaseScheduler)",
        )

    def handle(self, *args, **options):
        """Execute the command"""
        loglevel = options["loglevel"]
        scheduler = options["scheduler"]

        self.stdout.write(self.style.SUCCESS("Starting Celery Beat scheduler..."))
        self.stdout.write(f"Log level: {loglevel}")
        self.stdout.write(f"Scheduler: {scheduler}")

        # Build celery beat command
        cmd = [
            sys.executable,
            "-m",
            "celery",
            "-A",
            "config",
            "beat",
            "--loglevel",
            loglevel,
            "--scheduler",
            scheduler,
        ]

        try:
            # Start the beat scheduler
            subprocess.run(cmd, check=True)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Stopping Celery Beat scheduler..."))
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"Celery Beat scheduler failed: {e}"))
            return
