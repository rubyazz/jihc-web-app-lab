from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from diller.models import Car, Client, Transaction
from users.models import Employee
from .permissions import IsManager, IsAccountant, IsAdmin
from rest_framework.response import Response
from rest_framework.decorators import action
from djstripe.models import PaymentIntent
from .serializers import TransactionSerializer, CarListSerializer, CarDetailsSerializer, EmployeeListSerializer, EmployeeDetailsSerializer, ClientListSerializer, ClientDetailsSerializer
from rest_framework import status
import stripe

def home(request):
    data = {"message": "Welcome to the home page."}
    return JsonResponse(data)


class CarViewSet(ModelViewSet):
    """Car CRUD API"""

    queryset = Car.objects.all()
    serializer_class = CarListSerializer

    def get_serializer_class(self):
        if self.action in ("retrieve", "update"):
            return CarDetailsSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['post'])
    def sell_car(self, request, pk=None):
        car = self.get_object()

        if car.isSold:
            return Response({"error": "Car already sold."}, status=status.HTTP_400_BAD_REQUEST)

        transaction_serializer = TransactionSerializer(data={
            'car': car.id,
            'client': request.data.get('client_id'),
            'amount': car.price,
        })

        if transaction_serializer.is_valid():
            transaction_status = transaction_serializer.validated_data.get('status', 'approved_admin')

            if transaction_status == 'approved_admin':
                stripe.api_key = "sk_test_51OAZxFHMsqh1ECvorSjAjXlgMGNrFR5PyeY5KcwN0jzEJgebyccS6P9ltViNnBPgqieG7KQoyx0XVJ7CGeSs62ZQ00eskokOoO"

                # Create a payment intent
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

                return Response({"client_secret": payment_intent.client_secret, "message": "car is sold"})
            else:
                return Response({"error": "Transaction not approved by the required authority."},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": transaction_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class EmployeeViewSet(ModelViewSet):
    """Employee CRUD api"""

    queryset = Employee.objects.all()
    serializer_class = EmployeeListSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    @action(detail=True, methods=['post'])
    def approve_sale(self, request, pk=None):
        car = self.get_object()

        if not request.user.has_role('admin'):
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        transaction_serializer = TransactionSerializer(data={
            'car': car.id,
            'client': request.data.get('client_id'),
            'amount': car.price,
            'status': Transaction.APPROVED_ADMIN,
        })

        if transaction_serializer.is_valid():
            transaction_serializer.save()

            return Response({"message": "Admin approval successful."})
        else:
            return Response({"error": transaction_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

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

    @action(detail=True, methods=['post'])
    def approve_sale(self, request, pk=None):
        car = self.get_object()

        if not request.user.has_role('manager'):
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        transaction_serializer = TransactionSerializer(data={
            'car': car.id,
            'client': request.data.get('client_id'),
            'amount': car.price,
            'status': Transaction.APPROVED_MANAGER,
        })

        if transaction_serializer.is_valid():
            transaction_serializer.save()

            return Response({"message": "Manager approval successful."})
        else:
            return Response({"error": transaction_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

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

    @action(detail=True, methods=['post'])
    def approve_sale(self, request, pk=None):
        car = self.get_object()

        if not request.user.has_role('accountant'):
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        latest_transaction = car.transaction_set.order_by('-id').first()

        if not latest_transaction:
            return Response({"error": "No transaction found for the car."}, status=status.HTTP_400_BAD_REQUEST)

        if latest_transaction.status == Transaction.APPROVED_ACCOUNTANT:
            return Response({"error": "Transaction already approved by the accountant."},
                            status=status.HTTP_400_BAD_REQUEST)

        latest_transaction.status = Transaction.APPROVED_ACCOUNTANT
        latest_transaction.save()

        return Response({"message": "Accountant approval successful."})

    def get_queryset(self):
        return Car.objects.filter(isSold=True)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        total_price = sum([car.price for car in queryset])
        return Response({"total_price": total_price})
