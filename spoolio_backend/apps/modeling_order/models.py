from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from .. common import models as common_models
from .. user_profile import models as user_profile_models

from ... libs import models as libs_models


class ModelingOrder(libs_models.SoftDeleteModel):

    ORDER_STATUS_CHOICES = (
        ('reviewing', 'Reviewing'),
        ('estimating_price', 'Estimating price'),
        ('rejected', 'Rejected'),
        ('awaiting_payment', 'Awaiting Payment'),
        ('in_progress', 'In progress'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    )

    user_profile = models.ForeignKey(user_profile_models.UserProfile, blank=True, null=True, on_delete=models.SET_NULL)

    contact_email = models.EmailField()
    comment = models.TextField(blank=True, null=True)

    # Images and PDFs
    attachment_files = GenericRelation(common_models.AttachmentFile)
    attachment_images = GenericRelation(common_models.AttachmentImage)

    estimated_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    status = models.CharField(max_length=16, choices=ORDER_STATUS_CHOICES, default='reviewing')

    def __str__(self):
        return "{}: [{}] BY={} CONTACT_EMAIL={}".format(self.pk, self.created_at, self.user_profile.user.email if self.user_profile is not None and self.user_profile.user is not None else 'guest', self.contact_email )

