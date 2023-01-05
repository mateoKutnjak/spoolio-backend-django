from django.contrib.contenttypes.models import ContentType

import django_filters

from . import models


class ProductVariationOptionCombinationFilter(django_filters.FilterSet):
    class Meta:
        model = models.ProductVariationOptionCombination
        fields = ("options", "product")

    options = django_filters.ModelMultipleChoiceFilter(
        field_name="options",
        queryset=models.ProductVariationOption.objects.all(),
        conjoined=True  # Explanation:  https://github.com/carltongibson/django-filter/issues/595#issuecomment-270566521
    )
