from rest_framework import serializers

from . import models

from ..filament import serializers as filament_serializers


class PrintingMethodSerializer(serializers.ModelSerializer):

    supported_materials = filament_serializers.MaterialSerializer(read_only=True, many=True)

    class Meta:
        model = models.PrintingMethod
        fields = '__all__'


class PrinterTypeSerializer(serializers.ModelSerializer):

    printer_method = PrintingMethodSerializer(read_only=True)
    supported_materials = filament_serializers.MaterialSerializer(read_only=True, many=True)

    class Meta:
        model = models.PrinterType
        fields = '__all__'


class PrinterSerializer(serializers.ModelSerializer):

    type = PrinterTypeSerializer(read_only=True)

    class Meta:
        model = models.Printer
        fields = '__all__'