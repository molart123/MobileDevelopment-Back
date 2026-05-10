from django.db import models
from django.conf import settings
from datetime import timedelta
from django.utils import timezone


class GameProgress(models.Model):
    """
    Хранит игровой прогресс пользователя: таймер и количество яиц в час.
    Один пользователь = одна запись.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='game_progress',
        verbose_name="Пользователь"
    )

    # Когда можно будет забрать яйца в следующий раз
    next_accrual_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Следующее начисление"
    )

    # Сколько яиц накапливается за час
    eggs_per_hour = models.IntegerField(
        default=100,
        verbose_name="Яиц в час"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Игровой прогресс"
        verbose_name_plural = "Игровой прогресс"

    def __str__(self):
        return f"Прогресс: {self.user.first_name}"

    def get_available_eggs(self):
        """
        Считает, сколько яиц накопилось с момента last_accrual.
        """
        now = timezone.now()
        if now < self.next_accrual_at:
            return 0

        # Сколько часов прошло
        delta = now - self.next_accrual_at
        hours = delta.total_seconds() / 3600

        # Сколько яиц накопилось
        return int(hours * self.eggs_per_hour)