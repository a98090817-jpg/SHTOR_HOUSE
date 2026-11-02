from django.contrib import admin
from .models import Favorite, Product, QuoteRequest


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
