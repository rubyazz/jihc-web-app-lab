from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from diller.models import Car, Client
from users.models import Employee
from .permissions import IsManager, IsAccountant, IsAdmin
from rest_framework.response import Response
from rest_framework.decorators import action
from djstripe.models import PaymentIntent
from .serializers import TransactionSerializer
from rest_framework import status
import stripe

from .serializers import (
    CarListSerializer,
    CarDetailsSerializer,
    EmployeeListSerializer,
    EmployeeDetailsSerializer,
    ClientListSerializer,
    ClientDetailsSerializer,
)

def home(request):
    data = {"message": "Welcome to the home page."}
    return JsonResponse(data)


class CarViewSet(ModelViewSet):
    """Car CRUD api"""

    queryset = Car.objects.all()
    serializer_class = CarListSerializer
    # permission_classes = [IsAuthenticated, IsAdmin]


    def get_serializer_class(self):
        if self.action in ("retrieve", "update"):
            return CarDetailsSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['post'])
    def sell_car(self, request, pk=None):
        car = self.get_object()

        if car.isSold:
            return Response({"error": "Car already sold."}, status=status.HTTP_400_BAD_REQUEST)

        # Assuming you have a Transaction model and serializer
        transaction_serializer = TransactionSerializer(data={
            'car': car.id,
            'client': request.data.get('client_id'), 
            'amount': car.price,
        })

        if transaction_serializer.is_valid():
            stripe.api_key = "sk_test_51OAZxFHMsqh1ECvorSjAjXlgMGNrFR5PyeY5KcwN0jzEJgebyccS6P9ltViNnBPgqieG7KQoyx0XVJ7CGeSs62ZQ00eskokOoO"  # Replace with your actual secret key

            payment_intent = stripe.PaymentIntent.create(
                amount=int(car.price * 100),  
                currency='usd',
                payment_method_types=['card'],
                payment_method="pm_card_visa",  
                confirm=True,
            )

            car.isSold = True
            car.save()

            transaction_serializer.save()

            return Response({"client_secret": payment_intent.client_secret})
        else:
            return Response({"error": transaction_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class EmployeeViewSet(ModelViewSet):
    """Employee CRUD api"""

    queryset = Employee.objects.all()
    serializer_class = EmployeeListSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_serializer_class(self):
        if self.action in ("retrieve", "update"):
            return EmployeeDetailsSerializer
        return super().get_serializer_class()


class ClientViewSet(ModelViewSet):
    """Client CRUD api"""

    queryset = Client.objects.all()
    serializer_class = ClientListSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_serializer_class(self):
        if self.action in ("retrieve", "update"):
            return ClientDetailsSerializer
        return super().get_serializer_class()



class ManagerCarViewSet(ModelViewSet):
    """Manager CRUD api for cars"""

    queryset = Car.objects.all()
    serializer_class = CarListSerializer
    permission_classes = [IsManager]

    def get_serializer_class(self):
        if self.action in ("retrieve", "update"):
            return CarDetailsSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class AccountantViewSet(ModelViewSet):
    """Accountant CRUD api for sum of prices of sold cars"""

    serializer_class = CarListSerializer
    permission_classes = [IsAccountant]

    def get_queryset(self):
        return Car.objects.filter(isSold=True)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        total_price = sum([car.price for car in queryset])
        return Response({"total_price": total_price})
