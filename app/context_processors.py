"""Sayt bo'ylab administrator bildirishnomalarini taqdim etuvchi processor."""

from .models import AdminNotification


def admin_notifications(request):
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated or not user.is_staff:
        return {
            'admin_unread_count': 0,
            'admin_latest_notifications': [],
        }

    latest = (
        AdminNotification.objects.select_related('user', 'product', 'admin_message')
        .order_by('-created_at')
    )
    return {
        'admin_unread_count': latest.filter(is_read=False).count(),
        'admin_latest_notifications': list(latest[:7]),
    }
