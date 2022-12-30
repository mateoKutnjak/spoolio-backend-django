from rest_framework import serializers

from . import models

from .. user_profile import models as user_profile_models, serializers as user_profile_serializers


class ModelingOrderSerializer(serializers.ModelSerializer):

    user_profile = serializers.PrimaryKeyRelatedField(queryset=user_profile_models.UserProfile.objects.all(), required=False)

    class Meta:
        model = models.ModelingOrder
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['user_profile'] = user_profile_serializers.UserProfileSerializer(read_only=True)
        return super(ModelingOrderSerializer, self).to_representation(instance)