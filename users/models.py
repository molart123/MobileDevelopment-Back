from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    photo_url = models.URLField(blank=True, default="", verbose_name="Avatar URL")
    auth_date = models.DateTimeField(null=True, blank=True)

    # Баланс яиц (текущий)
    eggs_count = models.IntegerField(default=0, verbose_name="Eggs balance")
    # Всего заработано яиц за всё время
    total_eggs_count = models.IntegerField(default=0, verbose_name="Total eggs earned")
    # Яйца, заработанные сегодня
    today_eggs_count = models.IntegerField(default=0, verbose_name="Eggs earned today")
    # Дата последнего сброса today_eggs_count
    today_eggs_date = models.DateField(null=True, blank=True, verbose_name="Last reset date for today eggs")

    # Билеты для разбивания яиц (дублируем для быстрого доступа)
    tickets_count = models.IntegerField(default=0, verbose_name="Tickets")
    # Выполнены ли ежедневные задания
    is_daily_tasks_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} (@{self.username})"

    def reset_today_eggs_if_new_day(self):
        """Обнуляет today_eggs_count, если наступил новый день."""
        today = timezone.localdate()
        if self.today_eggs_date != today:
            self.today_eggs_count = 0
            self.today_eggs_date = today
            self.save(update_fields=['today_eggs_count', 'today_eggs_date'])