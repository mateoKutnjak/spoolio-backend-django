from rest_framework import serializers

from . import models


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Category
        fields = '__all__'


class BlogSerializer(serializers.ModelSerializer):

    category = CategorySerializer()

    class Meta:
        model = models.Blog
        fields = '__all__'
