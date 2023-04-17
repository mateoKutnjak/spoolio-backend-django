from rest_framework import serializers

from .. print_order import models as print_order_models, serializers as print_order_serializers


class PrintOrderUnitSlicerEstimationSerializer(print_order_serializers.PrintOrderUnitSerializer):

    # ? Disabling primary key requirement because it is not present yet
    order = serializers.PrimaryKeyRelatedField(queryset=print_order_models.PrintOrder.objects.all(), required=False)

    # ? Frontend unit model file identificator
    local_url = serializers.CharField(required=True, help_text="Used as ID to identify the print order unit od response to frontend")
