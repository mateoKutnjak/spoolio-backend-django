from rest_framework import serializers

from . import models

from ..print_order import serializers as print_order_serializers


class PrintingJobSerializer(serializers.ModelSerializer):

    print_order_unit = print_order_serializers.PrintOrderUnitSerializer(read_only=True)

    class Meta:
        model = models.PrintingJob
        fields = '__all__'