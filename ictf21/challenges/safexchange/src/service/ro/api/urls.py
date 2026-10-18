from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = [
    path('buycoin', views.buyCoinView, name='buyCoin'),
    path('sellcoin', views.sellCoinView, name='sellCoin'),
    path('buyflag', views.buyFlagView, name='buyFlag'),
    path('fetchbalances', views.fetchBalancesView, name='fetchBalances'),
]
