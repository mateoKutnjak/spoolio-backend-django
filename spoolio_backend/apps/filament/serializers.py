from rest_framework import serializers

from . import models


class ColorSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Color
        fields = '__all__'


class MaterialSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Material
        fields = '__all__'


class SpoolSerializer(serializers.ModelSerializer):

    material = MaterialSerializer()
    color = ColorSerializer()

    class Meta:
        model = models.Spool
        fields = '__all__'