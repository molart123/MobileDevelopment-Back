import random
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Ticket, InstantGift, PromoCode, PromoCodeUsage, Price, CommunityAccess, PromoCodeGift
from .serializers import (
    InstantGiftSerializer, PriceSerializer, CommunityAccessSerializer,
    TicketBuySerializer, PromoCodeSerializer, PromoCodeGiftSerializer
)


def get_price(setting_type):
    try:
        return Price.objects.get(setting_type=setting_type).price
    except Price.DoesNotExist:
        return 50


class InstantGiftBuyView(APIView):
    """Купить мгновенный подарок — случайный промокод."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.reset_today_eggs_if_new_day()
        price = get_price("INSTANT_GIFT_PRICE")

        if user.eggs_count < price:
            return Response({"detail": "Недостаточно яиц."}, status=status.HTTP_400_BAD_REQUEST)

        # Выбираем случайный неиспользованный промокод
        available_codes = PromoCodeGift.objects.filter(is_used=False)
        if not available_codes.exists():
            return Response({"detail": "Подарки закончились."}, status=status.HTTP_400_BAD_REQUEST)

        promo = random.choice(available_codes)
        promo.is_used = True
        promo.save()

        user.eggs_count -= price
        user.save(update_fields=['eggs_count'])

        gift = InstantGift.objects.create(
            user=user,
            name="Мгновенный подарок",
            description=promo.description,
            image=promo.image,
            promo_code=promo.code,
            expires_at=timezone.now() + timedelta(days=30)
        )

        return Response({
            "instant_gift": InstantGiftSerializer(gift).data,
            "tickets_count": user.tickets_count,
            "filler_gifts": []
        })