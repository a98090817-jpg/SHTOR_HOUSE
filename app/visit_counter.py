"""Sayt tashriflarini hech qachon nolga tushmaydigan qilib hisoblash.

Uch qavatli saqlash:
1. SQLite bazasidagi `SiteVisitCounter` — asosiy hisob.
2. Lokal `.visit-counter-floor` fayli — baza o'chib ketganda zaxira.
3. Abacus (bepul tashqi counter API) — Render kabi ephemeral hostingda
   baza yangilanganda ham hisobni tiklaydi.

Baza yangidan yaratilsa ham qiymat shu manbalarning eng kattasidan olinadi,
shuning uchun hisoblagich 0 ga qaytmaydi.
"""

import json
import logging
import os
import threading
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.conf import settings
from django.db import DatabaseError, IntegrityError
from django.db.models import F

from .models import SiteVisitCounter

logger = logging.getLogger(__name__)

_REMOTE_BUSY = object()
_remote_lock = threading.Lock()
_remote_confirmed = False
_remote_down_until = 0.0


def _remote_url():
    if not getattr(settings, 'VISIT_COUNTER_REMOTE_ENABLED', False):
        return None
    namespace = str(getattr(settings, 'VISIT_COUNTER_NAMESPACE', '') or '').strip()
    key = str(getattr(settings, 'VISIT_COUNTER_KEY', '') or '').strip()
    if len(namespace) < 3 or len(key) < 3:
        return None
    base = str(getattr(settings, 'VISIT_COUNTER_API_URL', '') or '').rstrip('/')
    if not base:
        return None
    return f'{base}/hit/{quote(namespace, safe="")}/{quote(key, safe="")}'


def _hit_remote(timeout=None):
    url = _remote_url()
    if not url:
        return None
    request = Request(
        url,
        headers={'User-Agent': 'SHTOR-HOUSE-visit-counter/1.0'},
    )
    try:
        with urlopen(
            request,
            timeout=timeout or getattr(settings, 'VISIT_COUNTER_TIMEOUT', 2.0),
        ) as response:
            payload = json.loads(response.read().decode('utf-8'))
        if not isinstance(payload, dict):
            return None
        value = int(payload.get('value'))
    except (HTTPError, URLError, OSError, ValueError, TypeError, AttributeError):
        return None
    return value if value >= 0 else None


def _hit_remote_once(timeout=None):
    if not _remote_lock.acquire(blocking=False):
        return _REMOTE_BUSY
    try:
        return _hit_remote(timeout=timeout)
    finally:
        _remote_lock.release()


def _sync_remote():
    global _remote_confirmed, _remote_down_until

    now = time.monotonic()
    if now < _remote_down_until:
        return None

    value = _hit_remote_once()
    if value is _REMOTE_BUSY:
        return None
    if value is None:
        _remote_down_until = now + max(
            1, int(getattr(settings, 'VISIT_COUNTER_RETRY_SECONDS', 60))
        )
        _remote_confirmed = False
        return None

    _remote_confirmed = True
    return value


def _hit_remote_async():
    global _remote_confirmed, _remote_down_until

    if time.monotonic() < _remote_down_until:
        return

    def worker():
        global _remote_confirmed, _remote_down_until

        value = _hit_remote_once()
        if value is _REMOTE_BUSY:
            return
        if value is None:
            _remote_down_until = time.monotonic() + max(
                1, int(getattr(settings, 'VISIT_COUNTER_RETRY_SECONDS', 60))
            )
            _remote_confirmed = False
        else:
            _remote_confirmed = True

    threading.Thread(
        target=worker,
        name='shtor-visit-counter',
        daemon=True,
    ).start()


def _floor_path():
    return Path(getattr(settings, 'VISIT_COUNTER_FLOOR_FILE'))


def _read_floor():
    if not getattr(settings, 'VISIT_COUNTER_FLOOR_ENABLED', False):
        return 0
    try:
        return max(0, int(_floor_path().read_text(encoding='utf-8').strip()))
    except (OSError, ValueError):
        return 0


def _write_floor(value):
    if not getattr(settings, 'VISIT_COUNTER_FLOOR_ENABLED', False):
        return
    try:
        path = _floor_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_name(
            f'{path.name}.{os.getpid()}.{threading.get_ident()}.tmp'
        )
        temp_path.write_text(str(max(0, int(value))), encoding='utf-8')
        temp_path.replace(path)
    except (OSError, ValueError):
        pass


def increment_visit_count():
    """Tashrifni +1 qiladi va hech qachon kamaymaydigan qiymatni qaytaradi."""
    floor = _read_floor()
    db_count = 0
    db_ok = True

    try:
        try:
            SiteVisitCounter.objects.get_or_create(pk=1)
        except IntegrityError:
            pass
        if floor > 0:
            SiteVisitCounter.objects.filter(pk=1, count__lt=floor).update(count=floor)
        SiteVisitCounter.objects.filter(pk=1).update(count=F('count') + 1)
        db_count = (
            SiteVisitCounter.objects.filter(pk=1)
            .values_list('count', flat=True)
            .first()
            or 0
        )
    except DatabaseError:
        db_ok = False
        db_count = max(floor + 1, 1)
        logger.warning('Tashrif hisoblagichini bazaga yozib bo\'lmadi.', exc_info=True)

    remote_value = None
    if getattr(settings, 'VISIT_COUNTER_REMOTE_ENABLED', False):
        try:
            if (
                not _remote_confirmed
                or db_count
                <= int(getattr(settings, 'VISIT_COUNTER_SYNC_THRESHOLD', 3))
            ):
                remote_value = _sync_remote()
                if remote_value is not None:
                    if db_ok:
                        SiteVisitCounter.objects.filter(
                            pk=1, count__lt=remote_value
                        ).update(count=remote_value)
                    db_count = max(db_count, remote_value)
            elif db_ok:
                _hit_remote_async()
        except DatabaseError:
            logger.warning(
                'Tashqi hisoblagich qiymatini bazaga yozib bo\'lmadi.',
                exc_info=True,
            )

    baseline = max(0, int(getattr(settings, 'VISIT_COUNTER_BASELINE', 0)))
    final_count = max(db_count, floor, remote_value or 0, baseline, 1)
    _write_floor(final_count)
    return final_count
