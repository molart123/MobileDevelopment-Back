import hmac
import hashlib
from datetime import datetime

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import UserBalanceSerializer


class TelegramAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_data = request.data.get('user')
        auth_date = request.data.get('auth_date')
        received_hash = request.data.get('hash')

        if not user_data or not auth_date or not received_hash:
            return Response(
                {"detail": "Missing fields: user, auth_date, hash"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if 'id' not in user_data:
            return Response(
                {"detail": "Missing user.id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка подписи Telegram
        bot_token = settings.TELEGRAM_BOT_TOKEN
        secret_key = hmac.new(
            b"WebAppData",
            bot_token.encode('utf-8'),
            hashlib.sha256
        ).digest()

        data_to_check = {}
        for key, value in request.data.items():
            if key != 'hash':
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        data_to_check[f"user[{subkey}]"] = str(subvalue)
                else:
                    data_to_check[key] = str(value)

        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(data_to_check.items())
        )
        computed_hash = hmac.new(
            secret_key,
            data_check_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        if computed_hash != received_hash:
            return Response(
                {"detail": "Invalid hash"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Создаём или обновляем пользователя
        user, created = CustomUser.objects.update_or_create(
            telegram_id=user_data['id'],
            defaults={
                'first_name': user_data.get('first_name', ''),
                'last_name': user_data.get('last_name', ''),
                'username': user_data.get('username', ''),
                'photo_url': user_data.get('photo_url', ''),
                'auth_date': datetime.fromtimestamp(int(auth_date)),
            }
        )

        refresh = RefreshToken.for_user(user)
        return Response({
            "status": "ok",
            "user": {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "first_name": user.first_name,
                "username": user.username,
                "balance": user.eggs_count,
            },
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "created": created,
        })


class UserBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user.reset_today_eggs_if_new_day()  # обнулим если нужно
        serializer = UserBalanceSerializer(user)
        return Response(serializer.data)