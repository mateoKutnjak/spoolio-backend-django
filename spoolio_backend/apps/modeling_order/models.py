from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import signals

from .. common import models as common_models
from .. user_profile import models as user_profile_models

from ... libs import models as libs_models, signals as libs_signals


class ItemType(models.Model):

    name = models.CharField(max_length=128)
    icon_name = models.CharField(max_length=64)

    def __str__(self) -> str:
        return self.name


class ItemAttribute(models.Model):

    name = models.CharField(max_length=128)
    description = models.CharField(max_length=128, blank=True)

    def __str__(self) -> str:
        return self.name
    

class OrderType(models.Model):

    name = models.CharField(max_length=128)
    icon_name = models.CharField(max_length=64)

    def __str__(self) -> str:
        return self.name


class ModelingOrder(libs_models.SoftDeleteModel):

    STATUS_REVIEWING = 'reviewing'
    STATUS_ESTIMATING_PRICE = 'estimating_price'
    STATUS_AWAITING_PAYMENT = 'awaiting_payment'
    STATUS_REJECTED = 'rejected'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'

    ORDER_STATUS_CHOICES = (
        (STATUS_REVIEWING, STATUS_REVIEWING.replace('_', ' ').capitalize()),
        (STATUS_ESTIMATING_PRICE, STATUS_ESTIMATING_PRICE.replace('_', ' ').capitalize()),
        (STATUS_AWAITING_PAYMENT, STATUS_AWAITING_PAYMENT.replace('_', ' ').capitalize()),
        (STATUS_REJECTED, STATUS_REJECTED.replace('_', ' ').capitalize()),
        (STATUS_IN_PROGRESS, STATUS_IN_PROGRESS.replace('_', ' ').capitalize()),
        (STATUS_SHIPPED, STATUS_SHIPPED.replace('_', ' ').capitalize()),
        (STATUS_DELIVERED, STATUS_DELIVERED.replace('_', ' ').capitalize()),
    )

    user_profile = models.ForeignKey(user_profile_models.UserProfile, blank=True, null=True, on_delete=models.SET_NULL)

    contact_email = models.EmailField()
    comment = models.TextField(blank=True, null=True)

    # Images and PDFs
    attachment_files = GenericRelation(common_models.AttachmentFile)
    attachment_images = GenericRelation(common_models.AttachmentImage)

    item_type = models.ForeignKey(ItemType, on_delete=models.SET_NULL, null=True)
    item_attributes = models.ManyToManyField(ItemAttribute)
    order_type = models.ForeignKey(OrderType, on_delete=models.SET_NULL, null=True)

    estimated_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, help_text="VAT will be added on this price")

    status = models.CharField(max_length=16, choices=ORDER_STATUS_CHOICES, default='reviewing')

    def __str__(self):
        return "{}: [{}] BY={} CONTACT_EMAIL={}".format(self.pk, self.created_at, self.user_profile.user.email if self.user_profile is not None and self.user_profile.user is not None else 'guest', self.contact_email )


signals.pre_save.connect(receiver=libs_signals.print_order_pre_save_signal, sender=ModelingOrder)
signals.post_save.connect(receiver=libs_signals.print_order_post_save_signal, sender=ModelingOrder)