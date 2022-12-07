from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers

from . import models


from .. user_profile import serializers as user_profile_serializers, models as user_profile_models


class PrintOrderSerializer(serializers.ModelSerializer):

    # user_profile = user_profile_serializers.UserProfileSerializer(many=False)

    class Meta:
        model = models.PrintOrder
        fields = '__all__'
        # extra_fields = ['user_profile']

    # def create(self, validated_data):
    #     # * First create nested object
    #     user_profile_data = validated_data.pop('user_profile')
    #     user_profile = user_profile_models.UserProfile.objects.create(**user_profile_data)
        
    #     # * Then connect it to main object through FK relationship
    #     print_order = models.PrintOrder.objects.create(user_profile=user_profile, **validated_data)
    #     return print_order


class PrintOrderUnitSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.OrderUnit
        fields = '__all__'


class AttachmentFileSerializer(serializers.ModelSerializer):

    content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.all(),
        slug_field='model',
    )

    class Meta:
        model = models.AttachmentFile
        fields = '__all__'
