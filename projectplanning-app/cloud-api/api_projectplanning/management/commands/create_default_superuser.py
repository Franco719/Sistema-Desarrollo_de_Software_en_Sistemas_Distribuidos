from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = "Crea un superusuario si no existen usuarios."

    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.exists():
            User.objects.create_superuser(
                username=os.environ.get("DJANGO_SUPERUSER_USERNAME"),
                email=os.environ.get("DJANGO_SUPERUSER_EMAIL"),
                password=os.environ.get("DJANGO_SUPERUSER_PASSWORD")
            )
            self.stdout.write(self.style.SUCCESS("✅ Superuser creado automáticamente"))
