# AutoDillerApp/models.py

from django.db import models
from django.contrib.auth.models import User

class Car(models.Model):
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    price = models.FloatField()
    isSold = models.BooleanField(default=False)

class Client(models.Model):
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    email = models.EmailField()
    phoneNumber = models.CharField(max_length=15)
