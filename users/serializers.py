from rest_framework import serializers
from .models import CustomUser


class TelegramUserDataSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField()
    last_name = serializers.CharField(allow_blank=True, required=False, default="")
    username = serializers.CharField(allow_blank=True, required=False, default="")
    photo_url = serializers.URLField(allow_blank=True, required=False, default="")


class TelegramAuthSerializer(serializers.Serializer):
    user = TelegramUserDataSerializer()
    auth_date = serializers.CharField()
    hash = serializers.CharField(required=False, allow_blank=True)


class UserBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'today_eggs_count',
            'eggs_count',
            'tickets_count',
            'is_daily_tasks_completed',
            'today_tickets_count',
            'total_eggs_count',
        ]
        read_only_fields = fields

    today_tickets_count = serializers.IntegerField(source='tickets_count', read_only=True)