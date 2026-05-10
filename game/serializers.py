from rest_framework import serializers
from .models import GameProgress


class TimerSerializer(serializers.ModelSerializer):
    is_pending = serializers.SerializerMethodField()
    available_eggs = serializers.SerializerMethodField()

    class Meta:
        model = GameProgress
        fields = ['next_accrual_at', 'eggs_per_cycle', 'cycle_hours', 'is_pending', 'available_eggs']

    def get_is_pending(self, obj):
        return obj.get_available_eggs() > 0

    def get_available_eggs(self, obj):
        return obj.get_available_eggs()


class UpdateTimerSerializer(serializers.Serializer):
    next_accrual_at = serializers.DateTimeField()