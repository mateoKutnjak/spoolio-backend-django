from rest_framework import serializers

from .. print_order import models as print_order_models, serializers as print_order_serializers


class PrintOrderUnitSlicerEstimationSerializer(print_order_serializers.PrintOrderUnitSerializer):

    order = serializers.PrimaryKeyRelatedField(queryset=print_order_models.PrintOrder.objects.all(), required=False)
