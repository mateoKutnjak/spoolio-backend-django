from rest_framework import serializers

from . import models


class ProductSerializer(serializers.ModelSerializer):

    comment_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = models.Product
        fields = '__all__'

    def get_comment_count(self, instance):
        return instance.comments.count()

    def get_like_count(self, instance):
        return instance.likes.count()