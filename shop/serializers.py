from rest_framework import serializers
from .models import InstantGift, Price, CommunityAccess, PromoCodeGift


class PromoCodeGiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCodeGift
        fields = ['code', 'description', 'image']


class InstantGiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstantGift
        fields = ['id', 'name', 'description', 'image', 'promo_code', 'expires_at', 'obtained_at']


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = ['setting_type', 'price']


class CommunityAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityAccess
        fields = ['has_community_access', 'purchased_at']


class TicketBuySerializer(serializers.Serializer):
    ticket_amount = serializers.IntegerField(min_value=1)


class PromoCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)