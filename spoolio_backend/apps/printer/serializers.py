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
    printer_count = serializers.SerializerMethodField()

    class Meta:
        model = models.PrinterType
        fields = '__all__'

    def get_printer_count(self, instance):
        return models.Printer.objects.filter(type=instance).count()


class PrinterSerializer(serializers.ModelSerializer):

    type = PrinterTypeSerializer(read_only=True)

    class Meta:
        model = models.Printer
        fields = '__all__'