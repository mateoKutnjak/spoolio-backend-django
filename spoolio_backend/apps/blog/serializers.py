from rest_framework import serializers

from dj_rest_auth.serializers import UserDetailsSerializer

from . import models


class BlogSerializer(serializers.ModelSerializer):

    author = UserDetailsSerializer()

    class Meta:
        model = models.Blog
        fields = '__all__'