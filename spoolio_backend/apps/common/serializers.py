from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers

from . import models

from .. authentication import serializers as auth_serializers


class UserFilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def get_queryset(self):
        request = self.context.get('request', None)
        queryset = super(UserFilteredPrimaryKeyRelatedField, self).get_queryset()
        if not request or not queryset:
            return None
        return queryset.filter(user=request.user)


class CommentSerializer(serializers.ModelSerializer):

    user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())
    like_count = serializers.SerializerMethodField()
    liked_by_me = serializers.SerializerMethodField()

    content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.all(),
        slug_field='model',
    )

    class Meta:
        model = models.Comment
        fields = '__all__'

    def get_like_count(self, instance):
        return instance.likes.filter(is_deleted=False).count()

    def get_liked_by_me(self, instance):
        try:
            models.Like.objects.get(
                user=self.context['request'].user, 
                content_type=ContentType.objects.get_for_model(type(instance)), 
                object_id=instance.id,
                is_deleted=False)
            return True
        except ObjectDoesNotExist:
            return False
        finally:
            return False

    def to_representation(self, instance):
        self.fields['user'] = auth_serializers.UserDetailsSerializer(read_only=True)
        return super(CommentSerializer, self).to_representation(instance)


class LikeSerializer(serializers.ModelSerializer):

    user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())

    content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.all(),
        slug_field='model',
    )

    class Meta:
        model = models.Like
        fields = '__all__'


class ShippingAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ShippingAddress
        fields = '__all__'


class BillingAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.BillingAddress
        fields = '__all__'


class AttachmentFileSerializer(serializers.ModelSerializer):

    content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.all(),
        slug_field='model',
    )

    class Meta:
        model = models.AttachmentFile
        fields = '__all__'


class AttachmentImageSerializer(serializers.ModelSerializer):

    content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.all(),
        slug_field='model',
    )

    class Meta:
        model = models.AttachmentImage
        fields = '__all__'


class ShippingMethodSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ShippingMethod
        fields = '__all__'