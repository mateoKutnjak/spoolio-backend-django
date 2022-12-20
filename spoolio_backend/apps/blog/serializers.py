from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers

from . import models

from .. authentication import serializers as auth_serializers
from .. common import models as common_models


class BlogSerializer(serializers.ModelSerializer):

    author = auth_serializers.UserDetailsSerializer()
    comment_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    liked_by_me = serializers.SerializerMethodField()

    class Meta:
        model = models.Blog
        fields = '__all__'

    def get_comment_count(self, instance):
        return instance.comments.count()

    def get_like_count(self, instance):
        return instance.likes.count()

    def get_liked_by_me(self, instance):
        user = self.context['request'].user
        
        if user.is_anonymous:
            return False
        
        try:
            common_models.Like.objects.get(
                user=user, 
                content_type=ContentType.objects.get_for_model(type(instance)), 
                object_id=instance.id)
            return True
        except ObjectDoesNotExist:
            return False
        except Exception:
            return False