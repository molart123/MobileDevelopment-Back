from django.db import models


class DailyTicketDistribution(models.Model):
    """Фиксирует факт распределения билетов за день, чтобы не начислить дважды."""
    date = models.DateField(unique=True)
    performed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Distribution for {self.date}"