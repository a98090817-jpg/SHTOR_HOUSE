from django.db import models
from django.utils.text import slugify
import uuid


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
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Product, self.name)
        super().save(*args, **kwargs)

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
