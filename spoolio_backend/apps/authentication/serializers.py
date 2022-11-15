from django.contrib.auth import get_user_model

from rest_framework import serializers

from dj_rest_auth.serializers import JWTSerializer as dj_rest_JWTSerializer
from dj_rest_auth.serializers import TokenSerializer as TT

class UserDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = '__all__'