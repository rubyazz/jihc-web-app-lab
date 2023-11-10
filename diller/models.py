# AutoDillerApp/models.py

from django.db import models
from django.contrib.auth.models import User

class Car(models.Model):
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    price = models.FloatField()
    isSold = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.model} for {self.price}"

class Client(models.Model):
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    email = models.EmailField()
    phoneNumber = models.CharField(max_length=15)


class Transaction(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.client} bought {self.car} for ${self.amount}"

#     {
#   "model": "BMW",
#   "year": 2000,
#   "price": 10,
#   "isSold": false,
#   "client_id": 1  // Replace with the actual client ID
# }
