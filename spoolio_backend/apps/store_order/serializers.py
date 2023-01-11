from django.db.models import Sum

from rest_framework import serializers

from . import models

from .. common import models as common_models, serializers as common_serializers
from .. store import models as store_models, serializers as store_serializers
from .. user_profile import models as user_profile_models, serializers as user_profile_serializers


class StoreOrderUnitSerializer(serializers.ModelSerializer):

    # * Set this to required=False so we can post 
    # * store order item nested inside parent 
    # * store order
    item = serializers.PrimaryKeyRelatedField(queryset=store_models.ProductVariationOptionCombination.objects.all(), required=False)

    order = serializers.ReadOnlyField(source='order.id')

    class Meta:
        model = models.StoreOrderUnit
        fields = ('order', 'quantity', 'item')
        depth=1

    def to_representation(self, instance):
        self.fields['item'] = store_serializers.ProductVariationOptionCombinationSerializer()
        return super().to_representation(instance)


class StoreOrderSerializer(serializers.ModelSerializer):

    items = StoreOrderUnitSerializer(source='storeorderunit_set', many=True, required=False)

    user_profile = serializers.PrimaryKeyRelatedField(queryset=user_profile_models.UserProfile.objects.all(), required=False)

    shipping_address = common_serializers.ShippingAddressSerializer(required=False)
    billing_address = common_serializers.BillingAddressSerializer(required=False)

    shipping_method = serializers.PrimaryKeyRelatedField(queryset=common_models.ShippingMethod.objects.all(), required=True)

    total_price = serializers.SerializerMethodField()

    class Meta:
        model = models.StoreOrder
        fields = '__all__'

    def create(self, validated_data):
        shipping_address_data = validated_data.pop('shipping_address')
        billing_address_data = validated_data.pop('billing_address')

        items_data = validated_data.pop('storeorderunit_set')

        shipping_address = common_models.ShippingAddress.objects.create(**shipping_address_data)
        billing_address = common_models.BillingAddress.objects.create(**billing_address_data)
        
        order = models.StoreOrder.objects.create(shipping_address=shipping_address, billing_address=billing_address, **validated_data)
        for item_data in items_data:
            models.StoreOrderUnit.objects.create(order=order, **item_data)
        return order

    def get_total_price(self, instance):
        return instance.items.all().aggregate(Sum('price'))['price__sum']

    def to_representation(self, instance):
        self.fields['user_profile'] = user_profile_serializers.UserProfileSerializer(read_only=True)
        self.fields['shipping_method'] = common_serializers.ShippingMethodSerializer(read_only=True)

        return super(StoreOrderSerializer, self).to_representation(instance)