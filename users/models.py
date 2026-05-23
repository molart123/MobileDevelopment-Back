from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid


class CustomUser(AbstractUser):
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    photo_url = models.URLField(blank=True, default="", verbose_name="Avatar URL")
    auth_date = models.DateTimeField(null=True, blank=True)

    eggs_count = models.IntegerField(default=0, verbose_name="Eggs balance")
    total_eggs_count = models.IntegerField(default=0, verbose_name="Total eggs earned")
    today_eggs_count = models.IntegerField(default=0, verbose_name="Eggs earned today")
    today_eggs_date = models.DateField(null=True, blank=True, verbose_name="Last reset date for today eggs")

    tickets_count = models.IntegerField(default=0, verbose_name="Tickets")
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
        today = timezone.localdate()
        if self.today_eggs_date != today:
            self.today_eggs_count = 0
            self.today_eggs_date = today
            self.save(update_fields=['today_eggs_count', 'today_eggs_date'])


class BotLoginSession(models.Model):
    """
    Сессия для входа через бота: /start login_<token>
    """
    token = models.CharField(max_length=64, unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('ready', 'Ready'), ('expired', 'Expired')],
        default='pending'
    )

    def is_expired(self):
        """TTL = 5 минут для pending"""
        if self.status == 'pending':
            return (timezone.now() - self.created_at).seconds > 300
        return False