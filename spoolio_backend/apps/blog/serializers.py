from rest_framework import serializers

from . import models

from .. authentication import serializers as auth_serializers


class BlogSerializer(serializers.ModelSerializer):

    author = auth_serializers.UserDetailsSerializer()
    comment_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = models.Blog
        fields = '__all__'

    def get_comment_count(self, instance):
        return instance.comments.count()

    def get_like_count(self, instance):
        return instance.likes.count()