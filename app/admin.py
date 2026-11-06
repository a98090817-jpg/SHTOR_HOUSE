from django.contrib import admin
from .models import (
    ConcurrentLoginSlot,
    Favorite,
    Product,
    QuoteRequest,
    SiteVisitCounter,
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'color', 'material', 'length_meters', 'origin', 'price', 'is_featured', 'is_active')
    list_filter = ('category', 'is_featured', 'is_active')
    search_fields = ('name', 'color', 'material')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'product', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('full_name', 'phone', 'product__name')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'product__name')


@admin.register(SiteVisitCounter)
class SiteVisitCounterAdmin(admin.ModelAdmin):
    list_display = ('pk', 'count', 'updated_at')
    readonly_fields = ('count', 'updated_at')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        # Hisoblagichni o'chirib 0 ga tushirishning oldini olamiz.
        return False


@admin.register(ConcurrentLoginSlot)
class ConcurrentLoginSlotAdmin(admin.ModelAdmin):
    list_display = ('slot_number', 'user', 'session_key', 'expires_at')
    readonly_fields = ('slot_number', 'user', 'session_key', 'expires_at')
    actions = ('release_slots',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description='Band login slotlarini bo\'shatish')
    def release_slots(self, request, queryset):
        queryset.update(user=None, session_key=None, expires_at=None)
        self.message_user(request, 'Login slotlari bo\'shatildi.')
