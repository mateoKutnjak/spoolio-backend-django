from django.contrib.contenttypes.models import ContentType

import django_filters

from . import models


# * This FilterSet class is created only to replace query
# * parameter 'category__pk' in url with 'category'
class BlogCategoryFilter(django_filters.FilterSet):

    category = django_filters.ModelChoiceFilter(
        field_name="category",
        queryset=models.Category.objects.all())

    class Meta:
        model = models.Category
        fields = ('category',)