# from api.users.serializers import UserSerializer
from rest_framework import serializers
from diller.models import Car, Client, Transaction
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


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        extra_kwargs = {
            'client': {'required': True},
        }


class ClientListSerializer(serializers.ModelSerializer):

    transaction = TransactionSerializer()

    class Meta:
        model = Client
        fields = (
            "firstName",
            "lastName",
            "gender",
            "email",
            "transaction",
            )
        extra_kwargs = {
        "transaction" : {"required":"False"}
        }


class ClientDetailsSerializer(serializers.ModelSerializer):

    transaction = TransactionSerializer()

    class Meta:
        model = Client
        fields = (
            "firstName",
            "lastName",
            "gender",
            "email",
            "transaction",
            )