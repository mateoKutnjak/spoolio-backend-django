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


class InfillSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Infill
        fields = '__all__'