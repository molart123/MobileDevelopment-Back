from django.contrib import admin
from .models import Price, PromoCodeGift, InstantGift


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('setting_type', 'price')


@admin.register(PromoCodeGift)
class PromoCodeGiftAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'is_used', 'created_at')
    list_filter = ('is_used',)
    search_fields = ('code', 'description')


@admin.register(InstantGift)
class InstantGiftAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'promo_code', 'obtained_at')
    list_filter = ('obtained_at',)
    search_fields = ('user__first_name', 'name', 'promo_code')