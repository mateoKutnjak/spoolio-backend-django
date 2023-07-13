from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import signals

from .. common import models as common_models
from .. store import models as store_models
from .. user_profile import models as user_profile_models

from ... libs import models as libs_models, signals as libs_signals


class StoreOrder(libs_models.SoftDeleteModel):

    STATUS_AWAITING_PAYMENT = 'awaiting_payment'
    STATUS_REJECTED = 'rejected'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'

    ORDER_STATUS_CHOICES = (
        (STATUS_AWAITING_PAYMENT, STATUS_AWAITING_PAYMENT.replace('_', ' ').capitalize()),
        (STATUS_REJECTED, STATUS_REJECTED.replace('_', ' ').capitalize()),
        (STATUS_IN_PROGRESS, STATUS_IN_PROGRESS.replace('_', ' ').capitalize()),
        (STATUS_SHIPPED, STATUS_SHIPPED.replace('_', ' ').capitalize()),
        (STATUS_DELIVERED, STATUS_DELIVERED.replace('_', ' ').capitalize()),
    )

    user_profile = models.ForeignKey(user_profile_models.UserProfile, blank=True, null=True, on_delete=models.SET_NULL)

    contact_email = models.EmailField()
    shipping_address = models.ForeignKey(common_models.ShippingAddress, on_delete=models.RESTRICT)
    billing_address = models.ForeignKey(common_models.BillingAddress, on_delete=models.RESTRICT)
    shipping_method = models.ForeignKey(common_models.ShippingMethod, null=True, on_delete=models.SET_NULL)

    items = models.ManyToManyField(store_models.ProductVariationOptionCombination, through='StoreOrderUnit')

    status = models.CharField(max_length=16, choices=ORDER_STATUS_CHOICES, default='awaiting_payment')

    def __str__(self):
        return "{}: [{}] BY={} CONTACT_EMAIL={}".format(self.pk, self.created_at, self.user_profile.user.email if self.user_profile is not None and self.user_profile.user is not None else 'guest', self.contact_email )


class StoreOrderUnit(libs_models.SoftDeleteModel):

    item = models.ForeignKey(store_models.ProductVariationOptionCombination, on_delete=models.CASCADE)
    order = models.ForeignKey(StoreOrder, on_delete=models.CASCADE)
    
    quantity = models.PositiveIntegerField()


signals.pre_save.connect(receiver=libs_signals.print_order_pre_save_signal, sender=StoreOrder)
signals.post_save.connect(receiver=libs_signals.print_order_post_save_signal, sender=StoreOrder)