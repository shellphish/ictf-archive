from django.shortcuts import render
from .serializers import *
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import viewsets,permissions,response, decorators, status
from django.core.exceptions import ObjectDoesNotExist

@decorators.api_view(["POST",])
@decorators.permission_classes([permissions.IsAuthenticated])
def buyCoinView(request):
    if request.method == "POST":
        serializer = BuyCoinSerializer(data=request.data)
        
        if not serializer.is_valid():
            return response.Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        user = request.user 
        resp = serializer.buyCoin(user)

        return response.Response(resp, status.HTTP_201_CREATED)


@decorators.api_view(["POST",])
@decorators.permission_classes([permissions.IsAuthenticated])
def sellCoinView(request):
    if request.method == "POST":
        serializer = SellCoinSerializer(data=request.data)

        if not serializer.is_valid():
            return response.Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
            
        user = request.user 
        resp = serializer.sellCoin(user)

        return response.Response(resp, status.HTTP_201_CREATED)



@decorators.api_view(["POST",])
@decorators.permission_classes([permissions.IsAuthenticated])
def buyFlagView(request):
    if request.method == "POST":
        serializer = BuyFlagSerializer(data=request.data)

        if not serializer.is_valid():
            return response.Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
            
        user = request.user 
        resp = serializer.buyFlag(user)

        return response.Response(resp, status.HTTP_201_CREATED)


@decorators.api_view(["GET",])
@decorators.permission_classes([permissions.IsAuthenticated])
def fetchBalancesView(request):
    if request.method == "GET":
        serializer = FetchBalancesSerializer(data=request.data)

        if not serializer.is_valid():
            return response.Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
            
        user = request.user 
        resp = serializer.fetchBalances(user)

        return response.Response(resp, status.HTTP_201_CREATED)