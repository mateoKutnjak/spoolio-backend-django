from rest_framework import serializers

from . import models

from .. authentication import serializers as auth_serializers


class BlogSerializer(serializers.ModelSerializer):

    author = auth_serializers.UserDetailsSerializer()

    class Meta:
        model = models.Blog
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Comment
        fields = '__all__'