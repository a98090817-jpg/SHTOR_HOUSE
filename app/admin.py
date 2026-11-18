from django.contrib import admin
from .models import (
    AdminMessage,
    AdminNotification,
    ConcurrentLoginSlot,
    Favorite,
    LoginRecord,
    Product,
    QuoteRequest,
    SiteVisitCounter,
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'color', 'material', 'length_meters', 'origin', 'price', 'view_count', 'is_featured', 'is_active')
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


@admin.register(LoginRecord)
class LoginRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'method', 'ip_address', 'created_at')
    list_filter = ('method', 'created_at')
    search_fields = ('user__username', 'user__email', 'ip_address')
    readonly_fields = ('user', 'method', 'ip_address', 'user_agent', 'created_at')


@admin.register(AdminMessage)
class AdminMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'product', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'message', 'product__name')


@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ('kind', 'sender_name', 'user', 'product', 'login_method', 'is_read', 'created_at')
    list_filter = ('kind', 'is_read', 'login_method', 'created_at')
    search_fields = ('sender_name', 'user__username', 'product__name')


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
