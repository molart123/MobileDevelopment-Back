from django.urls import path
from .views import TimerView, ClaimEggsView, ClickEggView

urlpatterns = [
    path('timer/', TimerView.as_view(), name='eggs_timer'),
    path('claim/', ClaimEggsView.as_view(), name='eggs_claim'),
    path('click/', ClickEggView.as_view(), name='eggs_click'),
]