# core/serializers.py
from rest_framework import serializers
from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer
from store.models import Customer


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'username', 'password',
                  'email', 'first_name', 'last_name']

# 1. Create a dedicated serializer for the Customer data


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['phone', 'birth_date', 'membership']
        # Users shouldn't be able to upgrade their own membership via PATCH!
        read_only_fields = ['membership']

# 2. Nest it inside the User Serializer


class UserSerializer(BaseUserSerializer):
    # Map this to the 'customer' related name. It handles both Read AND Write!
    customer_profile = CustomerProfileSerializer(
        source='customer', required=False)

    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'username', 'email',
                  'first_name', 'last_name', 'customer_profile']

    def update(self, instance, validated_data):
        # Extract the nested customer data
        customer_data = validated_data.pop('customer', None)

        # Update the base User (first_name, last_name, etc.)
        user = super().update(instance, validated_data)

        # Update the Customer profile
        if customer_data:
            customer, created = Customer.objects.get_or_create(user=user)
            for attr, value in customer_data.items():
                setattr(customer, attr, value)
            customer.save()

        return user
