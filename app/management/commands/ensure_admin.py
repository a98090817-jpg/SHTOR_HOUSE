from django.core.management.base import BaseCommand

from app.admin_account import ensure_admin_account


class Command(BaseCommand):
    help = "Standart SHTOR HOUSE administrator hisobini yaratadi yoki yangilaydi."

    def handle(self, *args, **options):
        user, created = ensure_admin_account()
        action = 'yaratildi' if created else 'yangilandi'
        self.stdout.write(
            self.style.SUCCESS(f"Administrator '{user.username}' {action}.")
        )
