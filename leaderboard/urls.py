from django.urls import path
from .views import TopEggsTodayView

urlpatterns = [
    path('account/top_eggs_today/', TopEggsTodayView.as_view(), name='top_eggs'),
]