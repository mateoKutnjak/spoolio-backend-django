from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.html import format_html

from ..common import models as common_models

from ...libs import models as libs_models


class ProductCategory(libs_models.SoftDeleteModel):

    name = models.CharField(max_length=64)

    def __str__(self):
        return "{}: {}".format(self.pk, self.name)


class ProductSubcategory(libs_models.SoftDeleteModel):

    name = models.CharField(max_length=64)
    
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)

    def __str__(self):
        return "{}: {}/{}".format(self.pk, self.category.name, self.name)


class Product(libs_models.SoftDeleteModel):

    title = models.CharField(max_length=256)
    description = models.TextField()

    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(ProductSubcategory, on_delete=models.CASCADE)

    comments = GenericRelation(common_models.Comment)
    likes = GenericRelation(common_models.Like)
    
    def __str__(self):
        return "{}: {} [{}/{}]".format(self.pk, self.title, self.category.name, self.subcategory.name)


class ProductVariation(libs_models.SoftDeleteModel):

    name = models.CharField(max_length=64)

    def __str__(self):
        return "{}: {}".format(self.pk, self.name)


class ProductVariationOption(libs_models.SoftDeleteModel):

    title = models.CharField(max_length=256)
    description = models.TextField()

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    type = models.ForeignKey(ProductVariation, on_delete=models.CASCADE)

    def __str__(self):
        return "{}: {}: {} [{}]".format(self.pk, self.type.name, self.title, self.product.title)


class ProductVariationOptionCombination(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    options = models.ManyToManyField(ProductVariationOption)

    price = models.PositiveIntegerField()
    sku = models.PositiveIntegerField()

    def __str__(self):
        m2m_formatted = "<br/> ".join(str(seg) for seg in self.options.all())
        return format_html("{}: {} <br/> <br/> PRICE={} <br/> SKU={} <br/><br/> Attributes: <br/> {}".format(self.pk, self.product.title, self.price, self.sku, m2m_formatted))


class ProductImage(libs_models.SoftDeleteModel):

    image = models.ImageField(upload_to="product_images")
    comment = models.TextField(blank=True, null=True)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return "{}: {} - {}".format(self.pk, self.product.title, self.comment)
