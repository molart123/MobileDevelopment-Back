from django.urls import path
from .views import (
    TelegramAuthView,
    TelegramLoginView,
    UserBalanceView,
    CustomTokenRefreshView,
)

urlpatterns = [
    path('telegram_auth/', TelegramAuthView.as_view(), name='telegram_auth'),
    path('telegram_login/', TelegramLoginView.as_view(), name='telegram_login'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('user/balance/', UserBalanceView.as_view(), name='user_balance'),
]