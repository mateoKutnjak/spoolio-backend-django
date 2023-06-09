from rest_framework import serializers

from . import models

from .. user_profile import models as user_profile_models, serializers as user_profile_serializers


class ItemAttributeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ItemAttribute
        fields = '__all__'

    
class ItemTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ItemType
        fields = '__all__'


class ModelingOrderSerializer(serializers.ModelSerializer):

    user_profile = serializers.PrimaryKeyRelatedField(queryset=user_profile_models.UserProfile.objects.all(), required=False)
    
    item_attributes = serializers.PrimaryKeyRelatedField(queryset=models.ItemAttribute.objects.all(), many=True)
    item_type = serializers.PrimaryKeyRelatedField(queryset=models.ItemType.objects.all())

    class Meta:
        model = models.ModelingOrder
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['user_profile'] = user_profile_serializers.UserProfileSerializer(read_only=True)
        self.fields['item_attributes'] = ItemAttributeSerializer(read_only=True, many=True)
        self.fields['item_type'] = ItemTypeSerializer(read_only=True)

        return super(ModelingOrderSerializer, self).to_representation(instance)