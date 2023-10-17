from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers
import logging

from dj_rest_auth.registration.serializers import RegisterSerializer

from ..invitation_token import models as invitation_token_models
from ..user_profile import models as user_profile_models, serializers as user_profile_serializers
from ..modeling_order import models as modeling_models
from ..print_order import models as print_models

logger = logging.getLogger(__name__)


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

            serializer = user_profile_serializers.UserProfileSerializer(
                most_recent_visitor, read_only=True, many=False)
            return serializer.data

        except ObjectDoesNotExist:
            return None


class InvitationTokenRequiredRegisterSerializer(RegisterSerializer):

    invitation_token = serializers.CharField(write_only=True)
    order_id = serializers.IntegerField(write_only=True)
    order_type = serializers.CharField(write_only=True)

    def validate_invitation_token(self, invitation_token):

        logger.info(invitation_token)
        try:
            invitation_token_obj = invitation_token_models.InvitationToken.objects.get(
                value=invitation_token
            )

            if invitation_token_obj.user:
                raise serializers.ValidationError(
                    "Invitation token is already used")

        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                "Invitation token does not exist")

        logger.info("Invitation token success")
        return invitation_token

    def validate_order_id(self, order_id):
        return order_id

    def validate_order_type(self, order_type):
        return order_type

    def save(self, request):

        logger.info("Save Entered!")
        user = super().save(request)

        invitation_token = self.validated_data.get('invitation_token')

        invitation_token_obj = invitation_token_models.InvitationToken.objects.get(
            value=invitation_token
        )
        invitation_token_obj.user = user
        invitation_token_obj.save()

        try:
            order_id = self.validated_data.get('order_id')
            order_type = self.validated_data.get('order_type')
            if order_type and order_id:
                if order_type == "modeling":
                    order = modeling_models.ModelingOrder.objects.get(
                        pk=order_id)
                    order.user_profile = user.id
                    order.save()
                elif order_type == "printing":
                    order = print_models.PrintOrder.objects.get(pk=order_id)
                    order.user_profile = user.id
                    order.save()
        except:
            raise serializers.ValidationError("Order part error")

        return user
