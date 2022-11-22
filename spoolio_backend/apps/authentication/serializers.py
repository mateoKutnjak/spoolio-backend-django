from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers

from ..user_profile import serializers as user_profile_serializers
from ..user_profile import models as user_profile_models

class UserDetailsSerializer(serializers.ModelSerializer):

    profile = serializers.SerializerMethodField(method_name='get_user_profile')

    class Meta:
        model = get_user_model()
        fields = '__all__'

    def get_user_profile(self, obj):
        try:
            most_recent_visitor = user_profile_models.UserProfile.objects.get(
                user_id=obj.id
            )

            serializer = user_profile_serializers.UserProfileSerializer(most_recent_visitor, read_only=True, many=False)
            return serializer.data

        except ObjectDoesNotExist:
            return None