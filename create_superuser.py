import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from app.admin_account import ensure_admin_account

user, created = ensure_admin_account()
action = 'yaratildi' if created else 'yangilandi'
print(f"Administrator '{user.username}' {action}.")
print("Kirish: /admin/")
