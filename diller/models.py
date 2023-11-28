# AutoDillerApp/models.py

from django.db import models
from django.contrib.auth.models import User
from users.models import Employee

class Car(models.Model):
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    price = models.FloatField()
    isSold = models.BooleanField(default=False)

    def process_transaction(self, client, amount, payment_method, requesting_user):
        # Create a transaction
        transaction = Transaction.objects.create(
            car=self, client=client, amount=amount, payment_method=payment_method
        )

        # Process transaction based on the requesting user's role
        if requesting_user.has_role('manager'):
            transaction.status = Transaction.APPROVED_MANAGER
        elif requesting_user.has_role('accountant'):
            transaction.status = Transaction.APPROVED_ACCOUNTANT
        elif requesting_user.has_role('admin'):
            transaction.status = Transaction.APPROVED_ADMIN

        transaction.save()
        return transaction

    def __str__(self):
        return f"{self.model} for {self.price}"



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
    client_user = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        max_length=10, choices=[('credit', 'Credit'), ('cash', 'Cash')],
        default='cash' 
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return f"{self.client_user} bought {self.car} for ${self.amount}, Status: {self.status}"

class Client(models.Model):
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    email = models.EmailField()
    phoneNumber = models.CharField(max_length=15)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True)