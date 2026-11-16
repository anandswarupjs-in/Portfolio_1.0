"""Management command: create or update the Django superuser from environment variables.

Usage:
    python manage.py ensure_admin

Required environment variables (all three must be set):
    DJANGO_SUPERUSER_USERNAME
    DJANGO_SUPERUSER_EMAIL
    DJANGO_SUPERUSER_PASSWORD

If any variable is missing the command prints a clear message and exits without
making any change to the database.  No credential is ever written to source code.
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the superuser from env vars, or update the password if the user already exists."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "").strip()
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "").strip()

        missing = [
            name
            for name, val in (
                ("DJANGO_SUPERUSER_USERNAME", username),
                ("DJANGO_SUPERUSER_EMAIL", email),
                ("DJANGO_SUPERUSER_PASSWORD", password),
            )
            if not val
        ]
        if missing:
            self.stdout.write(
                self.style.WARNING(
                    "ensure_admin: skipped – the following environment variable(s) are not set: %s"
                    % ", ".join(missing)
                )
            )
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "is_staff": True, "is_superuser": True},
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS("ensure_admin: superuser '%s' created." % username))
        else:
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS("ensure_admin: superuser '%s' password updated." % username))
