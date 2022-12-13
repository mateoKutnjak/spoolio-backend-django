from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers

from . import models

from .. authentication import serializers as auth_serializers


class CommentSerializer(serializers.ModelSerializer):

    user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())
    like_count = serializers.SerializerMethodField()

    content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.all(),
        slug_field='model',
    )

    class Meta:
        model = models.Comment
        fields = '__all__'

    def get_like_count(self, instance):
        return instance.likes.count()

    def to_representation(self, instance):
        self.fields['user'] = auth_serializers.UserDetailsSerializer(read_only=True)
        return super(CommentSerializer, self).to_representation(instance)