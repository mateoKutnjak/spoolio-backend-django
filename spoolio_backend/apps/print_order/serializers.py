from rest_framework import serializers

from . import models, serializers as print_order_serializers
from ..print_job.models import PrintingJob

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
    infill = serializers.PrimaryKeyRelatedField(queryset=models.PrintUnitInfill.objects.all())
    wall = serializers.PrimaryKeyRelatedField(queryset=models.PrintUnitWall.objects.all())
    wall_thickness = serializers.PrimaryKeyRelatedField(queryset=models.PrintUnitWallThickness.objects.all())
    infill_wall_combination = serializers.PrimaryKeyRelatedField(queryset=models.PrintUnitInfillWallCombination.objects.all(), required=False)
    job_ids = serializers.ListField(allow_null=True, required=False, child=serializers.IntegerField())

    def to_representation(self, instance):
        self.fields['spool'] = filament_serializers.SpoolSerializer(read_only=True)
        self.fields['infill'] = print_order_serializers.PrintUnitInfillSerializer(read_only=True)
        self.fields['wall'] = print_order_serializers.PrintUnitWallSerializer(read_only=True)
        self.fields['wall_thickness'] = print_order_serializers.PrintUnitWallThicknessSerializer(read_only=True)

        return super(PrintOrderUnitSerializer, self).to_representation(instance)
    
    def create(self, validated_data):
        job_ids = validated_data.pop('job_ids')

        unit = models.OrderUnit.objects.create(**validated_data)

        if job_ids:
            if len(job_ids) > 0:
                PrintingJob.objects.filter(pk__in=job_ids).update(
                    print_order_unit=unit,
                    status=PrintingJob.STATUS_REVIEWING
                )
        return unit

    class Meta:
        model = models.OrderUnit
        fields = '__all__'


class PrintOrderUnitPlaceholderSerializer(serializers.Serializer):

    quantity = serializers.IntegerField(min_value=1)
    material = filament_serializers.MaterialSerializer()
    estimated_time = serializers.IntegerField(min_value=1)


class PrintUnitInfillSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PrintUnitInfill
        fields = '__all__'

class QuantityMultiplierSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.QuantityMultiplier
        fields = '__all__'

class CostVariablesSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CostVariables
        fields = '__all__'


class PrintUnitWallSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PrintUnitWall
        fields = '__all__'


class PrintUnitWallThicknessSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PrintUnitWallThickness
        fields = '__all__'


class PrintUnitInfillWallCombinationSerializer(serializers.ModelSerializer):

    infill = serializers.PrimaryKeyRelatedField(queryset=models.PrintUnitInfill.objects.all())
    wall = serializers.PrimaryKeyRelatedField(queryset=models.PrintUnitWall.objects.all())

    class Meta:
        model = models.PrintUnitInfillWallCombination
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['infill'] = print_order_serializers.PrintUnitInfillSerializer(read_only=True)
        self.fields['wall'] = print_order_serializers.PrintUnitWallSerializer(read_only=True)

        return super(PrintUnitInfillWallCombinationSerializer, self).to_representation(instance)