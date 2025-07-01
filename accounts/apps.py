from django.apps import AppConfig
import os
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError, ProgrammingError

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'# accounts/apps.py

    def ready(self):
        # Only on production (DEBUG=False)
        if os.getenv("DJANGO_DEBUG", "False") == "True":
            return
        User = get_user_model()
        username = os.getenv("ADMIN_USERNAME")
        email    = os.getenv("ADMIN_EMAIL")
        password = os.getenv("ADMIN_PASSWORD")
        if not (username and email and password):
            return

        try:
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                # You could also log.info("Auto‑created superuser")
        except (OperationalError, ProgrammingError):
            # DB not yet ready / migrations not applied—ignore
            pass
