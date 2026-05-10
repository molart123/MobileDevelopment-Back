from django.contrib import admin
from .models import Price

@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('setting_type', 'price')