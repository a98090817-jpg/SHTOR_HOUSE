import getpass
import os
import sys

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if not password:
    if sys.stdin.isatty():
        password = getpass.getpass('Superuser password: ')
    else:
        raise SystemExit(
            'DJANGO_SUPERUSER_PASSWORD o\'rnatilmagan. '
            'Skriptni interaktiv rejimda ishga tushiring yoki env orqali parol bering.'
        )

if len(password) < 8:
    raise SystemExit('Xavfsizlik uchun superuser paroli kamida 8 belgidan iborat bo\'lsin.')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' muvaffaqiyatli yaratildi!")
else:
    print(f"Superuser '{username}' allaqachon mavjud.")