from django.contrib import admin
from .models import Price, PromoCodeGift, InstantGift


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('setting_type', 'price')


@admin.register(PromoCodeGift)
class PromoCodeGiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'gift_type', 'drop_chance', 'is_used', 'created_at')
    list_filter = ('gift_type', 'is_used')
    search_fields = ('name', 'code', 'description')
    fieldsets = (
        ('Основное', {
            'fields': ('name', 'description', 'image', 'gift_type', 'drop_chance')
        }),
        ('Промокод', {
            'fields': ('code',),
        }),
        ('Яйца', {
            'fields': ('eggs_amount',),
        }),
        ('Билеты', {
            'fields': ('tickets_amount',),
        }),
    )


@admin.register(InstantGift)
class InstantGiftAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'promo_code', 'obtained_at')
    list_filter = ('obtained_at',)
    search_fields = ('user__first_name', 'name', 'promo_code')