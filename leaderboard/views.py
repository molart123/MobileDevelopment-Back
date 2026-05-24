from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from users.models import CustomUser
from .models import DailyTicketDistribution
import datetime


class TopEggsTodayView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        yesterday = today - datetime.timedelta(days=1)

        # ====== РАСПРЕДЕЛЕНИЕ БИЛЕТОВ ЗА ВЧЕРАШНИЙ ДЕНЬ ======
        if not DailyTicketDistribution.objects.filter(date=yesterday).exists():
            # Берём топ-3 за вчера
            top3 = CustomUser.objects.filter(
                today_eggs_date=yesterday
            ).order_by('-today_eggs_count')[:3]

            rewards = {0: 50, 1: 20, 2: 10}  # 1, 2, 3 место
            for i, user in enumerate(top3):
                if i in rewards:
                    user.tickets_count += rewards[i]
                    user.save(update_fields=['tickets_count'])

            # Сбрасываем today_eggs_count всем, у кого вчерашняя дата
            CustomUser.objects.filter(today_eggs_date=yesterday).update(
                today_eggs_count=0,
                today_eggs_date=today
            )

            # Фиксируем распределение, чтобы не повторить
            DailyTicketDistribution.objects.create(date=yesterday)
        # ====================================================

        # Обновляем today_eggs для текущего пользователя
        user = request.user
        user.reset_today_eggs_if_new_day()

        # Топ-10 за сегодня
        top_users = CustomUser.objects.order_by('-today_eggs_count')[:10]
        leaders = []
        for u in top_users:
            leaders.append({
                "id": u.id,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "avatar": u.photo_url,
                "today_eggs_count": u.today_eggs_count,
                "message_link": f"https://t.me/{u.username}" if u.username else "",
            })

        # Позиция текущего пользователя
        position = CustomUser.objects.filter(
            today_eggs_count__gt=user.today_eggs_count
        ).count() + 1

        user_data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "avatar": user.photo_url,
            "today_eggs_count": user.today_eggs_count,
            "position": position,
        }

        return Response({
            "user": user_data,
            "top_users": leaders,
        })