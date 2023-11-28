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
            # 'status': Transaction.APPROVED_ADMIN, 
        })

        if transaction_serializer.is_valid():
            transaction = transaction_serializer.save()

            if transaction.status == Transaction.APPROVED_ADMIN:
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
    # permission_classes = [IsAuthenticated, IsAdmin]

    @action(detail=True, methods=['post'])
    def approve_sale(self, request, pk=None):
        car = self.get_object()

        if not request.user.has_role('admin'):
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        # USD price
        usd_price_api = "https://currency-converter18.p.rapidapi.com/api/v1/convert"

        querystring = {"from":"USD","to":"KZT","amount":"1"}

        headers = {
            "X-RapidAPI-Key": "d7af63a666mshc3f4a24426ace55p14ea0cjsn2e3c9e8fe3d9",
            "X-RapidAPI-Host": "currency-converter18.p.rapidapi.com"
        }
        try:
            response = requests.get(usd_price_api, headers=headers, params=querystring)
            if response.get('success'):
                converted_amount = response['result']['convertedAmount']
        except (requests.RequestException, ValueError):
            return Response({"error": "Failed to fetch actual USD price from the API."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        expected_usd_price = car.price * converted_amount 

        approval_threshold = 0.95 * actual_usd_price

        if expected_usd_price > approval_threshold:
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
        else:
            explanation = "The expected price is significantly lower than the actual price."
            latest_transaction = Transaction.objects.create(
                car=car,
                client=request.data.get('client_id'),
                amount=car.price,
                status=Transaction.REJECTED,
                explanation=explanation,
            )

            return Response({"error": f"Admin rejection. Explanation: {explanation}"}, status=status.HTTP_400_BAD_REQUEST)


    def get_serializer_class(self):
        if self.action in ("retrieve", "update"):
            return EmployeeDetailsSerializer
        return super().get_serializer_class()


class ClientViewSet(ModelViewSet):
    """Client CRUD api"""

    queryset = Client.objects.all()
    serializer_class = ClientListSerializer
    # permission_classes = [IsAuthenticated, IsAdmin]

    def get_serializer_class(self):
        if self.action in ("retrieve", "update"):
            return ClientDetailsSerializer
        return super().get_serializer_class()


class ManagerCarViewSet(ModelViewSet):
    """Manager CRUD api for cars"""

    queryset = Car.objects.all()
    serializer_class = CarListSerializer
    # permission_classes = [IsManager]

    @action(detail=True, methods=['post'])
    def approve_sale(self, request, pk=None):
        car = self.get_object()

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

        # if not car.transaction_set.exists():
        #     # If no transactions exist, automatically approve the sale by the manager
        #     transaction_serializer = TransactionSerializer(data={
        #         'car': car.id,
        #         'client': request.data.get('client_id'),
        #         'amount': car.price,
        #         'status': Transaction.APPROVED_MANAGER,
        #     })

        #     if transaction_serializer.is_valid():
        #         transaction_serializer.save()
        #         return Response({"message": "Manager approval successful."})
        #     else:
        #         return Response({"error": transaction_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        # elif transaction_serializer.payment_method == "credit":
        #     # If transactions exist, check if 80% or more credits are successfully closed
        #     successful_transactions = car.transaction_set.filter(status=Transaction.APPROVED_MANAGER).count()
        #     total_transactions = car.transaction_set.count()

        #     if (successful_transactions / total_transactions) >= 0.8:
        #         # If 80% or more credits are closed, proceed with approval
        #         transaction_serializer = TransactionSerializer(data={
        #             'car': car.id,
        #             'client': request.data.get('client_id'),
        #             'amount': car.price,
        #             'status': Transaction.APPROVED_MANAGER,
        #         })

        #         if transaction_serializer.is_valid():
        #             transaction_serializer.save()
        #             return Response({"message": "Manager approval successful."})
        #         else:
        #             return Response({"error": transaction_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        #     else:
        #         return Response({"error": "Manager cannot approve sale. Less than 80% credits closed."},
        #                         status=status.HTTP_400_BAD_REQUEST)

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
    queryset = Car.objects.all()
    serializer_class = CarListSerializer
    # permission_classes = [IsAccountant]

    @action(detail=True, methods=['post'])
    def approve_sale(self, request, pk=None):
        car = self.get_object()

        transaction_serializer = TransactionSerializer(data={
                'car': car.id,
                'client': request.data.get('client_id'),
                'amount': car.price,
                'status': Transaction.APPROVED_ACCOUNTANT,
            })
        if transaction_serializer.is_valid():
            transaction_serializer.save()
            return Response({"message": "Accountant approval successful."})
        else:
            return Response({"error": transaction_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        # latest_transaction = car.transaction_set.order_by('-id').first()

        # if not latest_transaction:
        #     return Response({"error": "No transaction found for the car."}, status=status.HTTP_400_BAD_REQUEST)

        # action = request.data.get('action', 'approve')

        # if action == 'approve':
        #     if latest_transaction.status == Transaction.APPROVED_ACCOUNTANT:
        #         return Response({"error": "Transaction already approved by the accountant."},
        #                         status=status.HTTP_400_BAD_REQUEST)

        #     latest_transaction.status = Transaction.APPROVED_ACCOUNTANT
        #     latest_transaction.save()

        #     return Response({"message": "Accountant approval successful."})
        # elif action == 'reject':
        #     explanation = request.data.get('explanation', '')

        #     if not explanation:
        #         return Response({"error": "Rejection explanation is required for rejection."},
        #                         status=status.HTTP_400_BAD_REQUEST)

        #     latest_transaction.status = Transaction.REJECTED
        #     latest_transaction.explanation = explanation
        #     latest_transaction.save()

        #     return Response({"message": f"Accountant rejection successful. Explanation: {explanation}"})
        # else:
        #     return Response({"error": "Invalid action specified."},
        #                     status=status.HTTP_400_BAD_REQUEST)



