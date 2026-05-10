from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/account/', include('users.urls')),
    path('api/v1/eggs/', include('game.urls')),
    path('api/v1/', include('shop.urls')),
    path('api/v1/', include('leaderboard.urls')),
]