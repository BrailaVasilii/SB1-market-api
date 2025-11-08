"""
Django management command to start Celery worker
Following Django best practices for management commands
"""
from django.core.management.base import BaseCommand
import subprocess
import sys


class Command(BaseCommand):
    """Start Celery worker with proper configuration"""

    help = 'Start Celery worker for asynchronous task processing'

    def add_arguments(self, parser):
        """Add command arguments"""
        parser.add_argument(
            '--loglevel',
            default='info',
            help='Logging level (default: info)'
        )
        parser.add_argument(
            '--concurrency',
            type=int,
            default=4,
            help='Number of concurrent worker processes (default: 4)'
        )
        parser.add_argument(
            '--queues',
            default='celery,email,maintenance',
            help='Comma-separated list of queues to process '
                 '(default: celery,email,maintenance)'
        )

    def handle(self, *args, **options):
        """Execute the command"""
        loglevel = options['loglevel']
        concurrency = options['concurrency']
        queues = options['queues']

        self.stdout.write(
            self.style.SUCCESS('Starting Celery worker...')
        )
        self.stdout.write(f'Log level: {loglevel}')
        self.stdout.write(f'Concurrency: {concurrency}')
        self.stdout.write(f'Queues: {queues}')

        # Build celery worker command
        cmd = [
            sys.executable, '-m', 'celery',
            '-A', 'config',
            'worker',
            '--loglevel', loglevel,
            '--concurrency', str(concurrency),
            '--queues', queues,
        ]

        try:
            # Start the worker
            subprocess.run(cmd, check=True)
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('Stopping Celery worker...')
            )
        except subprocess.CalledProcessError as e:
            self.stderr.write(
                self.style.ERROR(f'Celery worker failed: {e}')
            )
            return
