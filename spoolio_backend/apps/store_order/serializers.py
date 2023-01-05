from rest_framework import serializers

from . import models


class StoreOrderSerializer(serializers.ModelSerializer):

    products = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = models.StoreOrder
        fields = '__all__'

    def get_comment_count(self, instance):
        return instance.comments.filter(is_deleted=False).count()

    def get_like_count(self, instance):
        return instance.likes.filter(is_deleted=False).count()