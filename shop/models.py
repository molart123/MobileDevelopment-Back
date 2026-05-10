from django.db import models
from django.conf import settings


class Ticket(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class PromoCodeGift(models.Model):
    """База промокодов для подарков."""
    code = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.URLField(blank=True, default="")
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {'Использован' if self.is_used else 'Доступен'}"

    class Meta:
        verbose_name = "Промокод для подарка"
        verbose_name_plural = "Промокоды для подарков"


class InstantGift(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.URLField(blank=True, default="")
    promo_code = models.CharField(max_length=100, blank=True, default="")
    expires_at = models.DateTimeField(null=True, blank=True)
    obtained_at = models.DateTimeField(auto_now_add=True)


class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    eggs_reward = models.IntegerField(default=100)
    max_uses = models.IntegerField(default=1)
    used_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)


class PromoCodeUsage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)


class Price(models.Model):
    SETTING_TYPE_CHOICES = [
        ("TICKET_PRICE", "Ticket Price"),
        ("INSTANT_GIFT_PRICE", "Instant Gift Price"),
        ("COMMUNITY_ENTRY_PRICE", "Community Entry Price"),
    ]
    setting_type = models.CharField(max_length=50, unique=True, choices=SETTING_TYPE_CHOICES)
    price = models.IntegerField()


class CommunityAccess(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    has_community_access = models.BooleanField(default=False)
    purchased_at = models.DateTimeField(null=True, blank=True)