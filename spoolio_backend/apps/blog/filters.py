from django.contrib.contenttypes.models import ContentType

import django_filters

from . import models


class BlogFilter(django_filters.FilterSet):

    class Meta:
        model = models.Blog
        fields = ("category", "tags", )

    tags = django_filters.ModelMultipleChoiceFilter(
        field_name="tags",
        queryset=models.Tag.objects.all(),
        conjoined=True  # Explanation:  https://github.com/carltongibson/django-filter/issues/595#issuecomment-270566521
    )

    category = django_filters.ModelChoiceFilter(
        field_name="category",
        queryset=models.Category.objects.all())