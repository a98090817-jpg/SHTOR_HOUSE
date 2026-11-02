from django.contrib import messages
from django.contrib.auth import logout
from django.db import transaction
from django.shortcuts import redirect
from django.utils import timezone

from .models import ConcurrentLoginSlot


class ConcurrentLoginLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not self._claim_slot(request):
            logout(request)
            messages.error(
                request,
                'All 10 sign-in slots are currently in use. Please try again later.',
            )
            return redirect('login')

        return self.get_response(request)

    @staticmethod
    def _claim_slot(request):
        if request.session.session_key is None:
            request.session.save()

        session_key = request.session.session_key
        if session_key is None:
            return False

        now = timezone.now()
        expires_at = request.session.get_expiry_date()

        with transaction.atomic():
            slots = ConcurrentLoginSlot.objects.select_for_update()
            slots.filter(
                session_key__isnull=False,
                expires_at__lte=now,
            ).update(user=None, session_key=None, expires_at=None)

            existing_slot = slots.filter(session_key=session_key).first()
            if existing_slot is not None:
                if existing_slot.user_id != request.user.pk:
                    existing_slot.user = request.user
                    existing_slot.expires_at = expires_at
                    existing_slot.save(update_fields=['user', 'expires_at'])
                return True

            available_slot = slots.filter(session_key__isnull=True).first()
            if available_slot is None:
                return False

            available_slot.user = request.user
            available_slot.session_key = session_key
            available_slot.expires_at = expires_at
            available_slot.save(update_fields=['user', 'session_key', 'expires_at'])
            return True
