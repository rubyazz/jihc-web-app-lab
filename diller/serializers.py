# from api.users.serializers import UserSerializer
from rest_framework import serializers
from diller.models import Car, Client
from users.models import Employee


class CarListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Car
        fields = (
            "id",
            "model",
            "year", 
            "price", 
            "isSold",
        )


class CarDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Car
        fields = (
            "id",
            "model",
            "year", 
            "price", 
            "isSold",
        )


class EmployeeListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = (
            "id", 
            "first_name",
            "last_name", 
            "phone_number", 
            "nickname", 
            "email",
            "role", 
            "is_active",
        )


class EmployeeDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = (
            "id", 
            "first_name",
            "last_name", 
            "phone_number", 
            "nickname", 
            "email",
            "role", 
            "is_active", 
        )


class ClientListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = ("__all__")


class ClientDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = ("__all__")

