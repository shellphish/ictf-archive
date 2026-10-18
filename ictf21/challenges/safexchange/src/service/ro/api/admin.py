from django.contrib import admin
from .models import Money,Coin,Txid,Flag


@admin.register(Money)
class MoneyAdmin(admin.ModelAdmin):
    list_display = ['user','balance']


@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = ['user','balance']


@admin.register(Txid)
class TxidAdmin(admin.ModelAdmin):
    list_display = ['user','txid']


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ['flag']