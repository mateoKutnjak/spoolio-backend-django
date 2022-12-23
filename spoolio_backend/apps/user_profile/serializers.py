from django.contrib.auth import get_user_model

from rest_framework import serializers

from . import models


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Address
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):

    shipping_address = AddressSerializer(required=False)
    billing_address = AddressSerializer(required=False)

    class Meta:
        model = models.UserProfile
        fields = '__all__'

    def update(self, instance, validated_data):

        shipping_address_obj = None
        billing_address_obj = None

        if 'shipping_address' in validated_data:
            shipping_address_data = validated_data.pop('shipping_address')
            address_serializer = AddressSerializer()
            if instance.shipping_address:
                shipping_address_obj = address_serializer.update(instance.shipping_address, shipping_address_data)
            else:
                shipping_address_obj = address_serializer.create(shipping_address_data)

        if 'billing_address' in validated_data:
            billing_address_data = validated_data.pop('billing_address')
            address_serializer = AddressSerializer()

            if instance.billing_address:
                billing_address_obj = address_serializer.update(instance.billing_address, billing_address_data)
            else:
                billing_address_obj = address_serializer.create(billing_address_data)
        
        validated_data['shipping_address'] = shipping_address_obj
        validated_data['billing_address'] = billing_address_obj
        
        return super(self.__class__, self).update(instance, validated_data)