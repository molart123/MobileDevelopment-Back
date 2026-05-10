from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import GameProgress
from .serializers import TimerSerializer, UpdateTimerSerializer


class TimerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        progress, _ = GameProgress.objects.get_or_create(user=request.user)
        serializer = TimerSerializer(progress)
        return Response(serializer.data)

    def patch(self, request):
        progress, _ = GameProgress.objects.get_or_create(user=request.user)
        serializer = UpdateTimerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        new_time = serializer.validated_data['next_accrual_at']
        now = timezone.now()
        if new_time < now:
            return Response(
                {"detail": "Cannot set a past date."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if new_time > now + timedelta(days=7):
            return Response(
                {"detail": "Cannot set a date more than 7 days ahead."},
                status=status.HTTP_400_BAD_REQUEST
            )

        progress.next_accrual_at = new_time
        progress.save()
        return Response(TimerSerializer(progress).data)


class ClaimEggsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        progress, _ = GameProgress.objects.get_or_create(user=request.user)
        available = progress.get_available_eggs()
        if available <= 0:
            return Response(
                {"detail": "No eggs to claim."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        user.reset_today_eggs_if_new_day()
        user.eggs_count += available
        user.total_eggs_count += available
        user.today_eggs_count += available
        user.save(update_fields=['eggs_count', 'total_eggs_count', 'today_eggs_count'])

        progress.next_accrual_at = timezone.now()
        progress.save()

        return Response({
            "claimed_eggs": available,
            "new_balance": user.eggs_count,
        })