from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from diller.models import Car, Client
from users.models import Employee
from .permissions import IsManager, IsAccountant, IsAdmin
from rest_framework.response import Response

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
    permission_classes = [IsAuthenticated, IsAdmin]


    def get_serializer_class(self):
        if self.action in ("retrieve", "update"):
            return CarDetailsSerializer
        return super().get_serializer_class()



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
