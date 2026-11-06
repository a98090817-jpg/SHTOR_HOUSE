import os

from django.contrib.auth import get_user_model

# Standart administrator hisobi. Parol kodda ochiq saqlanmaydi — faqat hash.
# Agar DJANGO_ADMIN_PASSWORD env o'zgaruvchisi berilgan bo'lsa, o'sha ishlatiladi.
DEFAULT_ADMIN_USERNAME = 'Pardashop77'
DEFAULT_ADMIN_EMAIL = 'admin@shtorhouse.uz'
DEFAULT_ADMIN_PASSWORD_HASH = (
    'pbkdf2_sha256$1000000$qV1tC9CTRJ6zaXqtD1jV4I$'
    'JgHqZBnEWIW2JThGjJa3MBx9WWy7WHQ6xaoM2QxBkFg='
)


def ensure_admin_account():
    """Admin hisobini yaratadi yoki mavjudini yangilaydi.

    Har safar `migrate` bajarilganda chaqiriladi, shuning uchun baza yangidan
    yaratilsa ham administrator kirish imkoniyati yo'qolmaydi.
    """
    User = get_user_model()
    username = (
        os.environ.get('DJANGO_ADMIN_USERNAME', DEFAULT_ADMIN_USERNAME).strip()
        or DEFAULT_ADMIN_USERNAME
    )
    email = (
        os.environ.get('DJANGO_ADMIN_EMAIL', DEFAULT_ADMIN_EMAIL).strip()
        or DEFAULT_ADMIN_EMAIL
    )
    password = os.environ.get('DJANGO_ADMIN_PASSWORD')

    user = User.objects.filter(username__iexact=username).first()
    created = user is None
    if created:
        user = User(username=username)

    user.username = username
    user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    if password:
        user.set_password(password)
    else:
        # Standart parolni har safar tiklaymiz — hisob hech qachon yo'qolmaydi.
        user.password = DEFAULT_ADMIN_PASSWORD_HASH
    user.save()
    return user, created
