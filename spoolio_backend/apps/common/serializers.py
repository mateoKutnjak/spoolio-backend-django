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


class RatingSerializer(serializers.ModelSerializer):

    user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())

    content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.all(),
        slug_field='model',
    )

    class Meta:
        model = models.Rating
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['user'] = auth_serializers.UserDetailsSerializer(read_only=True)
        return super(RatingSerializer, self).to_representation(instance)


class ShippingAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ShippingAddress
        fields = '__all__'


class BillingAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.BillingAddress
        fields = '__all__'

    def validate(self, attrs):
        return super().validate(attrs)

    def validate(self, attrs):
        if attrs['type'] == models.BillingAddress.TYPE_INDIVIDUAL:

            # * For TYPE_INDIVIDUAL followind fields are required which
            # * are not set as required in models.py:
            # *
            # * first_name
            # * last_name
            # *
            # * Rest of the fields needed are required in models.py

            validation_errors = {}

            if not attrs.get('first_name'):
                validation_errors['first_name'] = 'This field is required'
            if not attrs.get('last_name'):
                validation_errors['last_name'] = 'This field is required'

            if validation_errors:
                raise serializers.ValidationError(validation_errors)
            
            return super().validate(attrs)
    
        elif attrs['type'] == models.BillingAddress.TYPE_COMPANY:

            # * For TYPE_COMPANY followind fields are required which
            # * are not set as required in models.py:
            # *
            # * company_name
            # * contact_first_name
            # * contact_last_name
            # * vat_id
            # *
            # * Rest of the fields needed are required in models.py

            validation_errors = {}

            if not attrs.get('company_name'):
                validation_errors['company_name'] = 'This field is required'
            if not attrs.get('contact_first_name'):
                validation_errors['contact_first_name'] = 'This field is required'
            if not attrs.get('contact_last_name'):
                validation_errors['contact_last_name'] = 'This field is required'
            if not attrs.get('vat_id'):
                validation_errors['vat_id'] = 'This field is required'

            if validation_errors:
                raise serializers.ValidationError(validation_errors)
            
            return super().validate(attrs)
        
        else:
            raise serializers.ValidationError("Billing address type not recognized")


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