from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver

from .models import ConcurrentLoginSlot


@receiver(user_logged_out)
def release_concurrent_login_slot(sender, request, user, **kwargs):
    if request is not None and request.session.session_key:
        ConcurrentLoginSlot.objects.filter(
            session_key=request.session.session_key
        ).update(user=None, session_key=None, expires_at=None)
