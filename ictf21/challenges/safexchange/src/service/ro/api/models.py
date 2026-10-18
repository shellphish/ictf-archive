from django.db import models
from django.contrib.auth.models import User

class Coin(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    balance = models.IntegerField()
    

class Money(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    balance = models.IntegerField()

class Txid(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    txid = models.CharField(max_length=11)

class Flag(models.Model):
    flag = models.CharField(max_length=75)
    