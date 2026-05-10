from django.urls import path
from .views import TelegramAuthView, UserBalanceView

urlpatterns = [
    path('telegram_auth/', TelegramAuthView.as_view(), name='telegram_auth'),
    path('user/balance/', UserBalanceView.as_view(), name='user_balance'),
]