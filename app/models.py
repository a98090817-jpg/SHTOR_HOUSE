from django.db import models
from django.utils import timezone
from django.utils.text import slugify
import mimetypes
import uuid

from .image_processing import BROWSER_SAFE_IMAGE_TYPES, normalize_product_image


def generate_unique_slug(model_class, name, slug_field='slug'):
    """Unikal slug yaratish: kirillcha uchun fallback va takrorlanmaslik kafolati."""
    base = slugify(name)
    if not base:
        # Kirillcha yoki boshqa slugify emas bo'lgan belgilar uchun UUID qisqartma
        base = 'product'
    slug = base
    counter = 1
    while model_class.objects.filter(**{slug_field: slug}).exists():
        counter += 1
        slug = f'{base}-{counter}'
    return slug


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('living_room', 'Living Room'),
        ('bedroom', 'Bedroom'),
        ('kitchen', 'Kitchen'),
        ('office', 'Office'),
        ('custom', 'Custom'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='living_room')
    color = models.CharField(max_length=100)
    material = models.CharField(max_length=100)
    length_meters = models.DecimalField(max_digits=7, decimal_places=2, default=1)
    origin = models.CharField(max_length=200, default='')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    # Rasmning baza nusxasi: Render kabi hostinglarda disk vaqtinchalik bo'ladi,
    # shu sababli fayl yo'qolsa ham rasm bazadan ko'rsatiladi.
    image_data = models.BinaryField(null=True, blank=True, editable=False)
    image_content_type = models.CharField(max_length=50, blank=True, default='')
    image_stored_at = models.DateTimeField(null=True, blank=True, editable=False)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    view_count = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Product, self.name)
        self._store_image_in_database()
        super().save(*args, **kwargs)

    def _store_image_in_database(self):
        """Rasm faylini bazaga nusxalaydi.

        Shu tufayli sayt qaysi qurilmadan ochilmasin va server qayta
        ishga tushsa ham mahsulot rasmi ko'rinib turadi.
        """
        if not self.image:
            return
        name = getattr(self.image, 'name', '') or ''
        if not name:
            return

        try:
            self.image.open('rb')
            self.image.seek(0)
            raw = self.image.read()
        except (FileNotFoundError, OSError, ValueError):
            # Diskdagi fayl yo'q (masalan, Render deploydan keyin) —
            # bazadagi avvalgi nusxani o'chirmaymiz.
            return
        finally:
            try:
                self.image.seek(0)
            except (OSError, ValueError):
                pass

        if not raw:
            return

        content_type = mimetypes.guess_type(name)[0] or ''
        if content_type not in BROWSER_SAFE_IMAGE_TYPES:
            try:
                normalized = normalize_product_image(self.image)
                raw = normalized.read()
                content_type = 'image/webp'
            except Exception:
                # O'girib bo'lmasa ham mahsulot saqlanishi kerak.
                content_type = content_type or 'application/octet-stream'

        self.image_data = raw
        self.image_content_type = content_type
        self.image_stored_at = timezone.now()

    def __str__(self):
        return self.name


class QuoteRequest(models.Model):
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quote_requests',
    )
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        product_name = self.product.name if self.product else '—'
        return f"{self.full_name} - {product_name}"


class SiteVisitCounter(models.Model):
    """Saytga tashriflar sonini doimiy saqlaydigan yagona yozuv (pk=1)."""
    count = models.PositiveBigIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site visit counter'
        verbose_name_plural = 'Site visit counter'

    def __str__(self):
        return f'{self.count} visits'

class Favorite(models.Model):
    # Foydalanuvchining sevimli mahsulotlari, bazada saqlanadi.
    user = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, related_name='favorites'
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class LoginRecord(models.Model):
    """Foydalanuvchi qaysi usulda tizimga kirganini saqlaydi.

    Administrator foydalanuvchilar faolligini kuzatishi uchun har bir kirish
    qayd etiladi: parol orqali yoki Google akkaunti orqali.
    """

    METHOD_CHOICES = [
        ('password', 'Password'),
        ('google', 'Google'),
    ]

    user = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, related_name='login_records'
    )
    method = models.CharField(
        max_length=20, choices=METHOD_CHOICES, default='password'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', '-created_at'])]

    def __str__(self):
        return f'{self.user.username} - {self.get_method_display()}'


class AdminMessage(models.Model):
    """Foydalanuvchidan administratorga yuborilgan shaxsiy xabar."""

    user = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_messages',
    )
    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_messages',
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.full_name} - {self.created_at:%d.%m.%Y %H:%M}'


class AdminNotification(models.Model):
    """Administrator uchun bildirishnoma (kirish, sevimlilar, xabarlar)."""

    KIND_CHOICES = [
        ('login', 'Login'),
        ('register', 'Registration'),
        ('favorite', 'Favorite'),
        ('message', 'Message'),
    ]

    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_notifications',
    )
    sender_name = models.CharField(max_length=200, blank=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_notifications',
    )
    admin_message = models.ForeignKey(
        AdminMessage,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
    )
    login_method = models.CharField(
        max_length=20, blank=True, choices=LoginRecord.METHOD_CHOICES
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['is_read', '-created_at'])]

    def __str__(self):
        return f'{self.get_kind_display()} - {self.sender_name or "—"}'


class ConcurrentLoginSlot(models.Model):
    slot_number = models.PositiveSmallIntegerField(unique=True)
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='concurrent_login_slots',
    )
    session_key = models.CharField(max_length=40, unique=True, null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['slot_number']

    def __str__(self):
        return f'Login slot {self.slot_number}'
