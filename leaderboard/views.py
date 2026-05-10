from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from users.models import CustomUser
from django.db.models import F


class TopEggsTodayView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user.reset_today_eggs_if_new_day()

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

        # Позиция текущего пользователя среди всех (по today_eggs_count)
        position = CustomUser.objects.filter(today_eggs_count__gt=user.today_eggs_count).count() + 1
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