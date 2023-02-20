from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers

from . import models


from .. common import models as common_models, serializers as common_serializers
from .. filament import models as filament_models, serializers as filament_serializers
from .. user_profile import serializers as user_profile_serializers, models as user_profile_models


class PrintOrderSerializer(serializers.ModelSerializer):

    user_profile = serializers.PrimaryKeyRelatedField(queryset=user_profile_models.UserProfile.objects.all(), required=False)

    shipping_address = common_serializers.ShippingAddressSerializer()
    billing_address = common_serializers.BillingAddressSerializer()

    shipping_method = serializers.PrimaryKeyRelatedField(queryset=common_models.ShippingMethod.objects.all(), required=True)

    unit_count = serializers.SerializerMethodField()

    class Meta:
        model = models.PrintOrder
        fields = '__all__'

    def create(self, validated_data):
        shipping_address_data = validated_data.pop('shipping_address')
        billing_address_data = validated_data.pop('billing_address')

        shipping_address = common_models.ShippingAddress.objects.create(**shipping_address_data)
        billing_address = common_models.BillingAddress.objects.create(**billing_address_data)

        print_order = models.PrintOrder.objects.create(shipping_address=shipping_address, billing_address=billing_address, **validated_data)
        return print_order

    def to_representation(self, instance):
        self.fields['user_profile'] = user_profile_serializers.UserProfileSerializer(read_only=True)
        self.fields['shipping_method'] = common_serializers.ShippingMethodSerializer(read_only=True)

        return super(PrintOrderSerializer, self).to_representation(instance)

    def get_unit_count(self, instance):
        return models.OrderUnit.objects.filter(order=instance.id).count()


class PrintOrderUnitSerializer(serializers.ModelSerializer):

    spool = serializers.PrimaryKeyRelatedField(queryset=filament_models.Spool.objects.all(), required=False)

    def to_representation(self, instance):
        self.fields['spool'] = filament_serializers.SpoolSerializer(read_only=True)

        return super(PrintOrderUnitSerializer, self).to_representation(instance)

    class Meta:
        model = models.OrderUnit
        fields = '__all__'
