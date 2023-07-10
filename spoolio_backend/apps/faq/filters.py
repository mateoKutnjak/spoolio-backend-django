from django.contrib.contenttypes.models import ContentType

import django_filters

from . import models


class BlogFilter(django_filters.FilterSet):

    class Meta:
        model = models.Blog
        fields = ("category", )

    category = django_filters.ModelChoiceFilter(
        field_name="category",
        queryset=models.Category.objects.all())