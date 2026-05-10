from rest_framework import serializers
from .models import GameProgress


class TimerSerializer(serializers.ModelSerializer):
    is_pending = serializers.SerializerMethodField()

    class Meta:
        model = GameProgress
        fields = ['next_accrual_at', 'is_pending']

    def get_is_pending(self, obj):
        return obj.get_available_eggs() > 0


class UpdateTimerSerializer(serializers.Serializer):
    next_accrual_at = serializers.DateTimeField()