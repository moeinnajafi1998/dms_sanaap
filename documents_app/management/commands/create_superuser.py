from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Creates a default superuser if not already created"

    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.filter(username="1001").exists():
            User.objects.create_superuser(
                username="1001",
                password="M123m321m",
                email="moeinnajafi1996@example.com"
            )
            self.stdout.write(self.style.SUCCESS('Superuser "1001" created.'))
        else:
            self.stdout.write('Superuser "1001" already exists.')
