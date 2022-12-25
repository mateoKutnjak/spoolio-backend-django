from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from ..filament import models as filament_models
from ..user_profile import models as user_profile_models

from ...libs import models as common_models


class AttachmentFile(models.Model):

    file = models.FileField(upload_to="attachment_files")
    comment = models.TextField()

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()


class AttachmentImage(models.Model):

    image = models.ImageField(upload_to="attachment_images")
    comment = models.TextField()

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()


class PrintOrder(common_models.SoftDeleteModel):

    ORDER_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In progress'),
        ('completed', 'Completed'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
    )

    user_profile = models.ForeignKey(user_profile_models.UserProfile, null=True, on_delete=models.SET_NULL)

    comment = models.TextField(blank=True, null=True)

    # Images and PDFs
    attachment_files = GenericRelation(AttachmentFile)
    attachment_images = GenericRelation(AttachmentImage)

    status = models.CharField(max_length=16, choices=ORDER_STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return "[{}] print order by {}".format(self.status, self.user_profile.email if self.user_profile is not None else 'guest')


class OrderUnit(models.Model):

    LENGTH_UNIT_CHOICES = {
        'inches': 'inches',
        'mms': 'mms'
    }

    comment = models.TextField(blank=True, null=True)

    material = models.ForeignKey(filament_models.Material, on_delete=models.CASCADE)
    color = models.ForeignKey(filament_models.Color, on_delete=models.CASCADE)
    infill = models.ForeignKey(filament_models.Infill, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()

    file = models.FileField(upload_to="print_order_files")

    attachment_files = GenericRelation(AttachmentFile)
    attachment_images = GenericRelation(AttachmentImage)

    length_unit = models.CharField(max_length=8)

    order = models.ForeignKey(PrintOrder, on_delete=models.CASCADE)


class ShippingMethod(models.Model):

    provider = models.CharField(max_length=64)
    description = models.CharField(max_length=128)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    available = models.BooleanField()

    def __str__(self) -> str:
        return "{} ({})".format(self.provider, self.description)