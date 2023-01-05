from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from .. common import models as common_models
from .. store import models as store_models
from .. user_profile import models as user_profile_models

from ... libs import models as libs_models


class StoreOrder(libs_models.SoftDeleteModel):

    ORDER_STATUS_CHOICES = (
        ('rejected', 'Rejected'),
        ('awaiting_payment', 'Awaiting Payment'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    )

    user_profile = models.ForeignKey(user_profile_models.UserProfile, blank=True, null=True, on_delete=models.SET_NULL)

    contact_email = models.EmailField()
    shipping_address = models.ForeignKey(common_models.ShippingAddress, on_delete=models.RESTRICT)
    billing_address = models.ForeignKey(common_models.BillingAddress, on_delete=models.RESTRICT)
    shipping_method = models.ForeignKey(common_models.ShippingMethod, null=True, on_delete=models.SET_NULL)
    
    items = models.ManyToManyField(store_models.ProductVariationOptionCombination)

    status = models.CharField(max_length=16, choices=ORDER_STATUS_CHOICES, default='reviewing')

    def __str__(self):
        return "{}: [{}] BY={} CONTACT_EMAIL={}".format(self.pk, self.created_at, self.user_profile.email if self.user_profile is not None else 'guest', self.contact_email )

