from rest_framework import serializers

from . import models


class PrintingJobSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PrintingJob
        fields = '__all__'