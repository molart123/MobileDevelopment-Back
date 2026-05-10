from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class EggClick(models.Model):
    """Запись о клике по яйцу."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    clicked_at = models.DateTimeField(auto_now_add=True)


class GameProgress(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='game_progress',
        verbose_name="Пользователь"
    )

    next_accrual_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Следующее начисление"
    )

    eggs_per_cycle = models.IntegerField(
        default=140,
        verbose_name="Яиц за цикл"
    )

    cycle_hours = models.IntegerField(
        default=4,
        verbose_name="Часов в цикле"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Игровой прогресс"
        verbose_name_plural = "Игровой прогресс"

    def __str__(self):
        return f"Прогресс: {self.user.first_name}"

    def get_available_eggs(self):
        now = timezone.now()
        if now >= self.next_accrual_at:
            return self.eggs_per_cycle
        return 0

    def click_egg(self):
        now = timezone.now()
        if now < self.next_accrual_at:
            self.next_accrual_at = self.next_accrual_at - timedelta(minutes=1)
            if self.next_accrual_at < now:
                self.next_accrual_at = now
            self.save()
            EggClick.objects.create(user=self.user)