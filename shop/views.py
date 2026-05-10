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
    TicketBuySerializer, PromoCodeSerializer
)


def get_price(setting_type):
    try:
        return Price.objects.get(setting_type=setting_type).price
    except Price.DoesNotExist:
        return 50


class TicketBuyView(APIView):
    """Купить билеты для разбивания яиц."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TicketBuySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        amount = serializer.validated_data['ticket_amount']
        price_per_ticket = get_price("TICKET_PRICE")
        total_cost = amount * price_per_ticket

        user = request.user
        user.reset_today_eggs_if_new_day()
        if user.eggs_count < total_cost:
            return Response({"detail": "Недостаточно яиц."}, status=status.HTTP_400_BAD_REQUEST)

        user.eggs_count -= total_cost
        user.tickets_count += amount
        user.save(update_fields=['eggs_count', 'tickets_count'])

        ticket, _ = Ticket.objects.get_or_create(user=user)
        ticket.amount += amount
        ticket.save()

        return Response({"tickets": user.tickets_count, "balance": user.eggs_count})


class InstantGiftBuyView(APIView):
    """Купить мгновенный подарок — получение конкретного промокода по выбранной карточке."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.reset_today_eggs_if_new_day()
        price = get_price("INSTANT_GIFT_PRICE")

        if user.eggs_count < price:
            return Response(
                {"detail": "Недостаточно яиц."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем ID или код карточки, которую выбрал пользователь
        card_id = request.data.get("card_id")
        card_code = request.data.get("card_code")

        try:
            if card_id:
                gift_card = PromoCodeGift.objects.get(id=card_id, is_used=False)
            elif card_code:
                gift_card = PromoCodeGift.objects.get(code=card_code, is_used=False)
            else:
                return Response(
                    {"detail": "Не выбрана карточка."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except PromoCodeGift.DoesNotExist:
            return Response(
                {"detail": "Подарок недоступен или уже использован."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Списываем яйца
        user.eggs_count -= price
        user.save(update_fields=['eggs_count'])

        # Помечаем промокод использованным
        gift_card.is_used = True
        gift_card.save()

        # Сохраняем подарок у пользователя
        gift = InstantGift.objects.create(
            user=user,
            name=gift_card.name if hasattr(gift_card, 'name') else "Мгновенный подарок",
            description=gift_card.description,
            image=gift_card.image,
            promo_code=gift_card.code,
            expires_at=timezone.now() + timedelta(days=30)
        )

        return Response({
            "instant_gift": InstantGiftSerializer(gift).data,
            "tickets_count": user.tickets_count,
            "filler_gifts": []
        })


class InstantGiftListView(APIView):
    """Список полученных подарков."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        gifts = InstantGift.objects.filter(user=request.user)
        return Response(InstantGiftSerializer(gifts, many=True).data)


class PromoCodeActivateView(APIView):
    """Активировать промокод."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PromoCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        code = serializer.validated_data['code']
        user = request.user
        user.reset_today_eggs_if_new_day()

        try:
            promo = PromoCode.objects.get(code=code, is_active=True)
        except PromoCode.DoesNotExist:
            return Response({"detail": "Промокод не найден."}, status=status.HTTP_404_NOT_FOUND)

        if promo.used_count >= promo.max_uses:
            return Response({"detail": "Промокод закончился."}, status=status.HTTP_400_BAD_REQUEST)
        if PromoCodeUsage.objects.filter(user=user, promo_code=promo).exists():
            return Response({"detail": "Вы уже использовали этот промокод."}, status=status.HTTP_400_BAD_REQUEST)

        PromoCodeUsage.objects.create(user=user, promo_code=promo)
        promo.used_count += 1
        promo.save()

        user.eggs_count += promo.eggs_reward
        user.total_eggs_count += promo.eggs_reward
        user.today_eggs_count += promo.eggs_reward
        user.save(update_fields=['eggs_count', 'total_eggs_count', 'today_eggs_count'])

        return Response({"reward": promo.eggs_reward, "balance": user.eggs_count})


class PriceListView(APIView):
    """Список цен."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        prices = Price.objects.all()
        data = PriceSerializer(prices, many=True).data
        expected = ["TICKET_PRICE", "INSTANT_GIFT_PRICE", "COMMUNITY_ENTRY_PRICE"]
        result = []
        for setting_type in expected:
            match = [p for p in data if p['setting_type'] == setting_type]
            if match:
                result.append(match[0])
            else:
                result.append({"setting_type": setting_type, "price": 0})
        return Response(result)


class CommunityAccessBuyView(APIView):
    """Купить доступ в комьюнити."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.reset_today_eggs_if_new_day()
        price = get_price("COMMUNITY_ENTRY_PRICE")
        if user.eggs_count < price:
            return Response({"detail": "Недостаточно яиц."}, status=status.HTTP_400_BAD_REQUEST)

        user.eggs_count -= price
        user.save(update_fields=['eggs_count'])

        access, _ = CommunityAccess.objects.get_or_create(user=user)
        access.has_community_access = True
        access.purchased_at = timezone.now()
        access.save()

        return Response(CommunityAccessSerializer(access).data)


class CommunityAccessStatusView(APIView):
    """Статус доступа в комьюнити."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        access, _ = CommunityAccess.objects.get_or_create(user=request.user)
        return Response(CommunityAccessSerializer(access).data)