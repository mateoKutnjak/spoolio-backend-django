from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers

from dj_rest_auth.registration.serializers import RegisterSerializer

from ..invitation_token import models as invitation_token_models
from ..user_profile import models as user_profile_models, serializers as user_profile_serializers


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
        

class InvitationTokenRequiredRegisterSerializer(RegisterSerializer):

    invitation_token = serializers.CharField(write_only=True)

    def validate_invitation_token(self, invitation_token):

        try:
            invitation_token_obj = invitation_token_models.InvitationToken.objects.get(
                value=invitation_token
            )

            if invitation_token_obj.user:
                raise serializers.ValidationError("Invitation token is already used") 

        except ObjectDoesNotExist:
            raise serializers.ValidationError("Invitation token does not exist") 

        return invitation_token

    def save(self, request):
        user = super().save(request)

        invitation_token = self.validated_data.get('invitation_token')
        invitation_token_obj = invitation_token_models.InvitationToken.objects.get(
            value=invitation_token
        )
        invitation_token_obj.user = user
        invitation_token_obj.save()

        return user