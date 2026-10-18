from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from .models import Coin,Money,Txid,Flag
from django.core.exceptions import ObjectDoesNotExist
from .txid import txidGenerator


class BuyCoinSerializer(serializers.Serializer):
    amount = serializers.IntegerField()

    def buyCoin(self,user):
        money = Money.objects.get(user=user)


        amount = self.validated_data['amount']

        if amount <= 0:
            raise serializers.ValidationError(
                {"error": "amount must be more than 0"})

        if money.balance < amount:
            raise serializers.ValidationError(
                {"error": f"sorry! you dont have enough money, your cash balance is :{money.balance}"})

        txid = Txid(user=user,txid=txidGenerator(amount))
        txid.save()

        coin = Coin.objects.get(user=user)

        money.balance -= amount
        coin.balance += amount
        money.save()
        coin.save()
        return {f'You bought {amount} coins successfully'}


class SellCoinSerializer(serializers.Serializer):
    amount = serializers.IntegerField()

    def sellCoin(self,user):
        coin = Coin.objects.get(user=user) 
        amount = self.validated_data['amount']

        if amount <= 0:
            raise serializers.ValidationError(
                {"error": "amount must be more than 0"})

        if coin.balance < amount:
            raise serializers.ValidationError(
                {"error": f"sorry! you dont have enough coins, your coin balance is :{coin.balance}"})

        txid = Txid(user=user,txid=txidGenerator(amount))
        txid.save()


        money = Money.objects.get(user=user)

        money.balance += amount
        coin.balance -= amount
        money.save()
        coin.save()
        return f"You have successfully sold {amount} coins"



class BuyFlagSerializer(serializers.Serializer):

    def buyFlag(self,user):
        coin = Coin.objects.get(user=user)
        money = Money.objects.get(user=user)
        if coin.balance < 137:
            raise serializers.ValidationError(
                {"error": "You need 137 coins to buy a flag"})

        coin.balance = 10
        money.balance = 10
        coin.save()
        money.save()
        flag = Flag.objects.all().last()
        return flag.flag




class FetchBalancesSerializer(serializers.Serializer):

    def fetchBalances(self,user):
        try:
            coin = Coin.objects.get(user=user)
        except ObjectDoesNotExist:
            c = Coin(user=user,balance=10)
            c.save()
            coin = Coin.objects.get(user=user)

        try:
            money = Money.objects.get(user=user)
        except ObjectDoesNotExist:
            m = Money(user=user,balance=10)
            m.save()
            money = Money.objects.get(user=user)

        return {"coin_balance":coin.balance,"money_balance":money.balance}