from django.db import models

from ...libs import models as common_models


class Product(common_models.SoftDeleteModel):

    title = models.CharField(max_length=256)
    description = models.TextField()

    picture = models.ImageField(upload_to='product_images/', null=True, blank=True)

    price = models.DecimalField(max_digits=24, decimal_places=2)
    
    def __str__(self):
        return "{}: [price {}]".format(self.title, self.price)