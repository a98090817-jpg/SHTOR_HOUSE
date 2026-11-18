"""Foydalanuvchi faolligi va administrator bildirishnomalari yordamchilari."""

import ipaddress

from django.contrib.auth import get_user_model
from django.db.models import Prefetch

from .models import AdminNotification, Favorite

NOTIFICATION_KINDS = {'login', 'register', 'favorite', 'message'}


def client_ip(request):
    """Foydalanuvchi IP manzilini proxy sarlavhalaridan ham aniqlaydi."""
    forwarded = (request.META.get('HTTP_X_FORWARDED_FOR') or '').split(',')[0].strip()
    candidate = forwarded or request.META.get('REMOTE_ADDR') or ''
    try:
        return str(ipaddress.ip_address(candidate))
    except ValueError:
        return None


def record_login(request, user, method='password'):
    """Tizimga kirishni qayd etadi (parol yoki Google)."""
    from .models import LoginRecord

    if method not in {'password', 'google'}:
        method = 'password'
    return LoginRecord.objects.create(
        user=user,
        method=method,
        ip_address=client_ip(request),
        user_agent=(request.META.get('HTTP_USER_AGENT') or '')[:255],
    )


def notify_admin(kind, user=None, sender_name='', product=None, admin_message=None, login_method=''):
    """Administrator uchun yangi bildirishnoma yaratadi."""
    if kind not in NOTIFICATION_KINDS:
        return None
    if login_method not in {'password', 'google'}:
        login_method = ''
    return AdminNotification.objects.create(
        kind=kind,
        user=user,
        sender_name=(sender_name or (user.username if user else ''))[:200],
        product=product,
        admin_message=admin_message,
        login_method=login_method,
    )


def user_auth_method(user, records=None):
    """Foydalanuvchining oxirgi kirish usulini qaytaradi.

    Eski Google foydalanuvchilarida parol umuman o'rnatilmagan bo'ladi,
    shu sababli bunday hisoblar ham Google akkaunt deb hisoblanadi.
    """
    if records is None:
        last_record = user.login_records.first()
    else:
        last_record = records[0] if records else None
    if last_record is not None:
        return last_record.method
    return 'google' if not user.has_usable_password() else 'password'


def build_user_directory(limit=None):
    """Foydalanuvchilar ro'yxati va umumiy statistikani tayyorlaydi."""
    user_model = get_user_model()
    users = list(
        user_model.objects.filter(is_staff=False)
        .order_by('-date_joined')
        .prefetch_related(
            Prefetch(
                'favorites',
                queryset=Favorite.objects.select_related('product').order_by('-created_at'),
            ),
            'login_records',
        )
    )

    for user in users:
        records = list(user.login_records.all())
        user.login_records_list = records
        user.login_total = len(records)
        user.last_login_record = records[0] if records else None
        user.login_method = user_auth_method(user, records)
        user.favorite_items = [fav for fav in user.favorites.all() if fav.product_id]
        user.favorite_total = len(user.favorite_items)
        user.is_blocked = not user.is_active

    stats = {
        'total_users': len(users),
        'google_users': sum(1 for user in users if user.login_method == 'google'),
        'password_users': sum(1 for user in users if user.login_method == 'password'),
        'blocked_users': sum(1 for user in users if user.is_blocked),
        'google_logins': sum(
            1
            for user in users
            for record in user.login_records_list
            if record.method == 'google'
        ),
        'password_logins': sum(
            1
            for user in users
            for record in user.login_records_list
            if record.method == 'password'
        ),
        'favorite_total': sum(user.favorite_total for user in users),
    }

    return (users[:limit] if limit else users), stats
