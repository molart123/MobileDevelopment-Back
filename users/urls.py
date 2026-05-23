from django.urls import path
from .views import (
    TelegramAuthView,
    TelegramLoginView,
    UserBalanceView,
    CustomTokenRefreshView,
    BotLoginInitView,
    BotLoginStatusView,
    telegram_webhook,   # импорт вебхука
)

urlpatterns = [
    path('telegram_auth/', TelegramAuthView.as_view(), name='telegram_auth'),
    path('telegram_login/', TelegramLoginView.as_view(), name='telegram_login'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('user/balance/', UserBalanceView.as_view(), name='user_balance'),
    path('bot_login/init/', BotLoginInitView.as_view(), name='bot_login_init'),
    path('bot_login/status/', BotLoginStatusView.as_view(), name='bot_login_status'),
    # Вебхук для Telegram-бота
    path('bot/webhook/', telegram_webhook, name='telegram_webhook'),
]