from django.contrib.auth import get_user_model

from rest_framework import serializers

from . import models


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Address
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):

    shipping_address = AddressSerializer(read_only=True)
    billing_address = AddressSerializer(read_only=True)

    class Meta:
        model = models.UserProfile
        fields = '__all__'