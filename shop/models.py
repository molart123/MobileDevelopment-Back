from django.db import models
from django.conf import settings


class Ticket(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class PromoCodeGift(models.Model):
    """База подарков с разными типами наград."""

    GIFT_TYPES = [
        ('PROMOCODE', 'Промокод'),
        ('EGGS', 'Яйца'),
        ('TICKETS', 'Билеты'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.URLField(blank=True, default="")
    gift_type = models.CharField(max_length=20, choices=GIFT_TYPES, default='PROMOCODE')
    code = models.CharField(max_length=100, blank=True, default="")
    eggs_amount = models.IntegerField(default=0)
    tickets_amount = models.IntegerField(default=0)
    drop_chance = models.FloatField(default=10.0, help_text="Шанс выпадения в процентах")
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_gift_type_display()})"

    class Meta:
        verbose_name = "Подарок"
        verbose_name_plural = "Подарки"


class InstantGift(models.Model):
    """Полученные пользователем подарки (промокоды)."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.URLField(blank=True, default="")
    promo_code = models.CharField(max_length=100, blank=True, default="")
    expires_at = models.DateTimeField(null=True, blank=True)
    obtained_at = models.DateTimeField(auto_now_add=True)


class PromoCode(models.Model):
    """Промокоды для активации пользователем."""
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