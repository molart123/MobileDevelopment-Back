import hmac
import hashlib
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from .models import CustomUser
from .serializers import UserBalanceSerializer


class TelegramAuthView(APIView):
    """
    Авторизация через Telegram Mini App (initDataUnsafe).
    """
    permission_classes = [AllowAny]

    def post(self, request):
        user_data = request.data.get('user')
        auth_date = request.data.get('auth_date')
        received_hash = request.data.get('hash')

        # Проверка наличия полей
        if not user_data or not auth_date or not received_hash:
            return Response(
                {"code": "invalid_telegram_hash",
                 "detail": "Missing fields: user, auth_date, hash"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if 'id' not in user_data:
            return Response(
                {"code": "invalid_telegram_hash",
                 "detail": "Missing user.id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка auth_date (не старше 24 часов)
        try:
            auth_timestamp = int(auth_date)
        except (ValueError, TypeError):
            return Response(
                {"code": "invalid_telegram_hash",
                 "detail": "auth_date must be a valid timestamp"},
                status=status.HTTP_400_BAD_REQUEST
            )

        now_timestamp = int(timezone.now().timestamp())
        if now_timestamp - auth_timestamp > 86400:
            return Response(
                {"code": "auth_date_expired",
                 "detail": "Authentication data is older than 24 hours"},
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
                {"code": "invalid_telegram_hash",
                 "detail": "Hash mismatch"},
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
                'auth_date': datetime.fromtimestamp(auth_timestamp),
            }
        )

        if not user.is_active:
            return Response(
                {"code": "inactive_user",
                 "detail": "User account is inactive"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Создаём игровой прогресс для нового пользователя
        from game.models import GameProgress

        GameProgress.objects.get_or_create(
            user=user,
            defaults={
                'next_accrual_at': timezone.now() + timedelta(hours=4),
                'eggs_per_cycle': 140,
                'cycle_hours': 4
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


class TelegramLoginView(APIView):
    """
    Авторизация через Telegram Login Widget (сайт/APK).
    """
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get('id')
        first_name = request.data.get('first_name')
        auth_date = request.data.get('auth_date')
        received_hash = request.data.get('hash')

        if not user_id or not first_name or not auth_date or not received_hash:
            return Response(
                {"code": "invalid_telegram_hash",
                 "detail": "Missing fields: id, first_name, auth_date, hash"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка срока auth_date (не старше 24 часов)
        try:
            auth_timestamp = int(auth_date)
        except (ValueError, TypeError):
            return Response(
                {"code": "invalid_telegram_hash",
                 "detail": "auth_date must be a valid timestamp"},
                status=status.HTTP_400_BAD_REQUEST
            )

        now_timestamp = int(timezone.now().timestamp())
        if now_timestamp - auth_timestamp > 86400:
            return Response(
                {"code": "auth_date_expired",
                 "detail": "Authentication data is older than 24 hours"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка hash
        bot_token = settings.TELEGRAM_BOT_TOKEN
        secret_key = hmac.new(
            b"WebAppData",
            bot_token.encode('utf-8'),
            hashlib.sha256
        ).digest()

        data_to_check = {}
        for key, value in request.data.items():
            if key != 'hash':
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
                {"code": "invalid_telegram_hash",
                 "detail": "Hash mismatch"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Создаём или обновляем пользователя
        user, created = CustomUser.objects.update_or_create(
            telegram_id=user_id,
            defaults={
                'first_name': first_name,
                'last_name': request.data.get('last_name', ''),
                'username': request.data.get('username', ''),
                'photo_url': request.data.get('photo_url', ''),
                'auth_date': datetime.fromtimestamp(auth_timestamp),
            }
        )

        if not user.is_active:
            return Response(
                {"code": "inactive_user",
                 "detail": "User account is inactive"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Создаём игровой прогресс
        from game.models import GameProgress

        GameProgress.objects.get_or_create(
            user=user,
            defaults={
                'next_accrual_at': timezone.now() + timedelta(hours=4),
                'eggs_per_cycle': 140,
                'cycle_hours': 4
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


class CustomTokenRefreshView(TokenRefreshView):
    """Поддерживает оба ключа: refresh и refresh_token."""
    def post(self, request, *args, **kwargs):
        if 'refresh_token' in request.data and 'refresh' not in request.data:
            request.data['refresh'] = request.data['refresh_token']
        return super().post(request, *args, **kwargs)


class UserBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user.reset_today_eggs_if_new_day()
        serializer = UserBalanceSerializer(user)
        return Response(serializer.data)