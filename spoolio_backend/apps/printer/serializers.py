from rest_framework import serializers

from . import models

from ..filament import serializers as filament_serializers


class PrintingMethodSerializer(serializers.ModelSerializer):

    supported_materials = filament_serializers.MaterialSerializer(read_only=True, many=True)
    printer_type_picture = serializers.SerializerMethodField()

    class Meta:
        model = models.PrintingMethod
        fields = '__all__'

    def get_printer_type_picture(self, instance):
        # * Fetch picture URL of PrinterType of PrinterMethod
        request = self.context.get('request')
        first_printer_type = models.PrinterType.objects.filter(printing_method=instance).first()
        return request.build_absolute_uri(first_printer_type.picture.url) if first_printer_type is not None else None

class PrinterTypeSerializer(serializers.ModelSerializer):

    printing_method = PrintingMethodSerializer(read_only=True)
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