from django.contrib.contenttypes.models import ContentType

import django_filters

from . import models


class ContentTypeFilter(django_filters.FilterSet):
    class Meta:
        model = models.Comment
        fields = ("content_type", "object_id")

    content_type = django_filters.ModelChoiceFilter(
        field_name="content_type",
        to_field_name="model",
        queryset=ContentType.objects.all(),
    )