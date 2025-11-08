from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Create user groups for the application'

    def handle(self, *args, **options):
        # Create moderators group
        moderators_group, created = Group.objects.get_or_create(name='moderators')
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created "moderators" group')
            )
        else:
            self.stdout.write(
                self.style.WARNING('"moderators" group already exists')
            )
            
        self.stdout.write(
            self.style.SUCCESS('Groups setup completed')
        )