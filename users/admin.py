from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'first_name', 'telegram_id', 'eggs_count', 'tickets_count', 'is_active',
                    'created_at')
    list_filter = ('is_active', 'is_staff', 'created_at')
    search_fields = ('username', 'first_name', 'telegram_id')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Личная информация', {'fields': ('first_name', 'last_name', 'email', 'telegram_id', 'photo_url')}),
        ('Игровые данные', {'fields': ('eggs_count', 'total_eggs_count', 'today_eggs_count', 'tickets_count',
                                       'is_daily_tasks_completed')}),
        ('Разрешения', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Даты', {'fields': ('last_login', 'auth_date', 'date_joined', 'created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at', 'date_joined', 'last_login')