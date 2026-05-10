from django.urls import path
from .views import (
    TicketBuyView, InstantGiftBuyView, InstantGiftListView,
    PromoCodeActivateView, PriceListView,
    CommunityAccessBuyView, CommunityAccessStatusView
)

urlpatterns = [
    path('tickets/buy/', TicketBuyView.as_view(), name='tickets_buy'),
    path('instant_gift/buy/', InstantGiftBuyView.as_view(), name='instant_gift_buy'),
    path('instant_gift/obtained/', InstantGiftListView.as_view(), name='instant_gift_list'),
    path('promo_code/activate/', PromoCodeActivateView.as_view(), name='promo_activate'),
    path('price/', PriceListView.as_view(), name='price_list'),
    path('community_access/buy/', CommunityAccessBuyView.as_view(), name='community_buy'),
    path('community_access/status/', CommunityAccessStatusView.as_view(), name='community_status'),
]