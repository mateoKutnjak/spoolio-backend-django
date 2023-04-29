from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers

from . import models

from .. authentication import serializers as auth_serializers
from .. common import models as common_models


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Category
        fields = '__all__'


class SubcategorySerializer(serializers.ModelSerializer):

    category = CategorySerializer()

    class Meta:
        model = models.Subcategory
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Tag
        fields = '__all__'


class BlogSerializer(serializers.ModelSerializer):

    author = auth_serializers.UserDetailsSerializer()
    
    category = CategorySerializer()
    subcategory = SubcategorySerializer()
    tags = TagSerializer(many=True)

    comment_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    
    liked_by_me = serializers.SerializerMethodField()

    class Meta:
        model = models.Blog
        fields = '__all__'

    def get_comment_count(self, instance):
        return instance.comments.filter(is_deleted=False).count()

    def get_like_count(self, instance):
        return instance.likes.all().count()

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