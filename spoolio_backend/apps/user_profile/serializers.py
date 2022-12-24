from django.contrib.auth import get_user_model

from rest_framework import serializers

from . import models

from ..common import serializers as common_serializers


class UserProfileSerializer(serializers.ModelSerializer):

    shipping_address = common_serializers.ShippingAddressSerializer(required=False)
    billing_address = common_serializers.BillingAddressSerializer(required=False)

    class Meta:
        model = models.UserProfile
        fields = '__all__'

    def update(self, instance, validated_data):

        if 'shipping_address' in validated_data:
            shipping_address_data = validated_data.pop('shipping_address')
            address_serializer = common_serializers.ShippingAddressSerializer()
            if instance.shipping_address:
                shipping_address_obj = address_serializer.update(instance.shipping_address, shipping_address_data)
            else:
                shipping_address_obj = address_serializer.create(shipping_address_data)

            validated_data['shipping_address'] = shipping_address_obj

        if 'billing_address' in validated_data:
            billing_address_data = validated_data.pop('billing_address')
            address_serializer = common_serializers.BillingAddressSerializer()

            if instance.billing_address:
                billing_address_obj = address_serializer.update(instance.billing_address, billing_address_data)
            else:
                billing_address_obj = address_serializer.create(billing_address_data)
        
            validated_data['billing_address'] = billing_address_obj
        
        return super(self.__class__, self).update(instance, validated_data)