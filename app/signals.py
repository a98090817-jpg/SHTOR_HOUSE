import logging

from django.contrib.auth.signals import user_logged_out
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import ConcurrentLoginSlot

logger = logging.getLogger(__name__)


@receiver(user_logged_out)
def release_concurrent_login_slot(sender, request, user, **kwargs):
    if request is not None and request.session.session_key:
        ConcurrentLoginSlot.objects.filter(
            session_key=request.session.session_key
        ).update(user=None, session_key=None, expires_at=None)


@receiver(post_migrate)
def ensure_admin_after_migrate(sender, **kwargs):
    """Baza qayta yaratilganda ham admin hisobi avtomatik tiklanadi."""
    if getattr(sender, 'name', None) != 'app':
        return
    try:
        from .admin_account import ensure_admin_account

        ensure_admin_account()
    except Exception:
        # Migratsiyani to'xtatib qo'ymaymiz; xato logga yoziladi.
        logger.exception('Administrator hisobini avtomatik yaratib bo\'lmadi.')
