from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from ..common import models as common_models
from ..filament import models as filament_models
from ..user_profile import models as user_profile_models

from ...libs import models as libs_models


class PrintOrder(libs_models.SoftDeleteModel):

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
    attachment_files = GenericRelation(common_models.AttachmentFile)
    attachment_images = GenericRelation(common_models.AttachmentImage)

    status = models.CharField(max_length=16, choices=ORDER_STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return "{}: [{}] BY={} STATUS={}".format(self.pk, self.created_at, self.user_profile.email if self.user_profile is not None else 'guest', self.status )


class OrderUnit(libs_models.SoftDeleteModel):

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

    attachment_files = GenericRelation(common_models.AttachmentFile)
    attachment_images = GenericRelation(common_models.AttachmentImage)

    length_unit = models.CharField(max_length=8)

    order = models.ForeignKey(PrintOrder, on_delete=models.CASCADE)

    def __str__(self):
        return "{}: [{}] {} ATTRIBUTES={},{},{},{}".format(self.pk, self.created_at, self.file, self.material.name, self.color.name, self.infill.percentage*100, self.length_unit)
