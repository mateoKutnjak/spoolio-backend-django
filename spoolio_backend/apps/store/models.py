from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from ..common import models as common_models

from ...libs import models as libs_models


class Product(libs_models.SoftDeleteModel):

    title = models.CharField(max_length=256)
    description = models.TextField()

    picture = models.ImageField(upload_to='product_images/', null=True, blank=True)

    price = models.DecimalField(max_digits=24, decimal_places=2)

    comments = GenericRelation(common_models.Comment)
    likes = GenericRelation(common_models.Like)
    
    def __str__(self):
        return "{}: [price {}]".format(self.title, self.price)