# AutoDillerApp/models.py

from django.db import models
from django.contrib.auth.models import User

class Car(models.Model):
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    price = models.FloatField()
    isSold = models.BooleanField(default=False)

    def process_transaction(self, client, amount, requesting_user):
        # Создаем заявку
        transaction = Transaction.objects.create(car=self, client=client, amount=amount)

        # Отправляем заявку менеджеру
        if requesting_user.has_role('manager'):
            transaction.status = Transaction.APPROVED_MANAGER
            transaction.save()

        # Отправляем заявку бухгалтеру
        elif requesting_user.has_role('accountant'):
            transaction.status = Transaction.APPROVED_ACCOUNTANT
            transaction.save()

        # Отправляем заявку админу
        elif requesting_user.has_role('admin'):
            transaction.status = Transaction.APPROVED_ADMIN
            transaction.save()

        return transaction

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
    PENDING = 'pending'
    APPROVED_MANAGER = 'approved_manager'
    APPROVED_ACCOUNTANT = 'approved_accountant'
    APPROVED_ADMIN = 'approved_admin'
    REJECTED = 'rejected'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED_MANAGER, 'Approved by Manager'),
        (APPROVED_ACCOUNTANT, 'Approved by Accountant'),
        (APPROVED_ADMIN, 'Approved by Admin'),
        (REJECTED, 'Rejected'),
    ]

    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return f"{self.client} bought {self.car} for ${self.amount}, Status: {self.status}"


# {
#   "model": "BMW",
#   "year": 2000,
#   "price": 10,
#   "isSold": false,
#   "client_id": 1  // Replace with the actual client ID
# }

# {
#   "model": "Mercedes",
#   "year": 2023,
#   "price": 10000.0,
#   "isSold": false,
#   "client_id": 1 
# }

# https://dashboard.stripe.com/login?redirect=%2Ftest%2Fpayments%2Fpi_3OGg9HHMsqh1ECvo1GTHWwdt