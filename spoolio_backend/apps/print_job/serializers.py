from rest_framework import serializers

from . import models

from ..filament import serializers as filament_serializers
from ..print_order import serializers as print_order_serializers


class PrintingJobSerializer(serializers.ModelSerializer):

    print_order_unit = print_order_serializers.PrintOrderUnitSerializer(read_only=True)

    class Meta:
        model = models.PrintingJob
        fields = '__all__'


# * This serializer is used for estimation of printing jobs when
# * order is not created yet. Because of that units are also not
# * stored in database so we use placeholder class to handle only
# * most important data for estimation of print job times
class PrintingJobPlaceholderSerializer(serializers.ModelSerializer):

    quantity = serializers.IntegerField(min_value=1)
    material = filament_serializers.MaterialSerializer()
    estimated_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = models.PrintingJob
        fields = '__all__'