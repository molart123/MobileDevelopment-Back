from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Ticket, InstantGift, PromoCode, PromoCodeUsage, Price, CommunityAccess
from .serializers import (
    InstantGiftSerializer, PriceSerializer, CommunityAccessSerializer,
    TicketBuySerializer, PromoCodeSerializer
)

# Хелпер для получения цен из базы (с fallback)
def get_price(setting_type):
    try:
        return Price.objects.get(setting_type=setting_type).price
    except Price.DoesNotExist:
        return 50  # fallback, лучше логировать ошибку


class TicketBuyView(APIView):
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
            return Response({"detail": "Not enough eggs."}, status=status.HTTP_400_BAD_REQUEST)

        user.eggs_count -= total_cost
        user.tickets_count += amount
        user.save(update_fields=['eggs_count', 'tickets_count'])

        ticket, _ = Ticket.objects.get_or_create(user=user)
        ticket.amount += amount
        ticket.save()

        return Response({"tickets": user.tickets_count, "balance": user.eggs_count})


class InstantGiftBuyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.reset_today_eggs_if_new_day()
        price = get_price("INSTANT_GIFT_PRICE")
        if user.eggs_count < price:
            return Response({"detail": "Not enough eggs."}, status=status.HTTP_400_BAD_REQUEST)

        user.eggs_count -= price
        user.save(update_fields=['eggs_count'])

        gift = InstantGift.objects.create(
            user=user,
            name="Instant Gift",
            description="A random gift",
            promo_code="PROMO123",
            expires_at=timezone.now() + timezone.timedelta(days=30)
        )

        return Response({
            "instant_gift": InstantGiftSerializer(gift).data,
            "tickets_count": user.tickets_count,
            "filler_gifts": []  # можно добавить заглушки
        })


class InstantGiftListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        gifts = InstantGift.objects.filter(user=request.user)
        return Response(InstantGiftSerializer(gifts, many=True).data)


class PromoCodeActivateView(APIView):
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
            return Response({"detail": "Promo code not found."}, status=status.HTTP_404_NOT_FOUND)

        if promo.used_count >= promo.max_uses:
            return Response({"detail": "Promo code exhausted."}, status=status.HTTP_400_BAD_REQUEST)
        if PromoCodeUsage.objects.filter(user=user, promo_code=promo).exists():
            return Response({"detail": "You already used this promo code."}, status=status.HTTP_400_BAD_REQUEST)

        PromoCodeUsage.objects.create(user=user, promo_code=promo)
        promo.used_count += 1
        promo.save()

        user.eggs_count += promo.eggs_reward
        user.total_eggs_count += promo.eggs_reward
        user.today_eggs_count += promo.eggs_reward
        user.save(update_fields=['eggs_count', 'total_eggs_count', 'today_eggs_count'])

        return Response({"reward": promo.eggs_reward, "balance": user.eggs_count})


class PriceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        prices = Price.objects.all()
        # Фронт ждёт ровно три объекта, если каких-то нет – добавляем заглушки
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
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.reset_today_eggs_if_new_day()
        price = get_price("COMMUNITY_ENTRY_PRICE")
        if user.eggs_count < price:
            return Response({"detail": "Not enough eggs."}, status=status.HTTP_400_BAD_REQUEST)

        user.eggs_count -= price
        user.save(update_fields=['eggs_count'])

        access, _ = CommunityAccess.objects.get_or_create(user=user)
        access.has_community_access = True
        now = timezone.now()
        access.purchased_at = now
        access.save()

        return Response(CommunityAccessSerializer(access).data)


class CommunityAccessStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        access, _ = CommunityAccess.objects.get_or_create(user=request.user)
        return Response(CommunityAccessSerializer(access).data)