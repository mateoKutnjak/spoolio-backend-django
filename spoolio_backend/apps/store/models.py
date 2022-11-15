from django.contrib.auth import get_user_model
from django.db import models

from ...libs import models as common_models


class Product(common_models.SoftDeleteModel):

    title = models.CharField(max_length=256)
    description = models.TextField()

    price = models.DecimalField(max_digits=24, decimal_places=2)
    
    def __str__(self):
        return "{}: [price {}]".format(self.title, self.price)