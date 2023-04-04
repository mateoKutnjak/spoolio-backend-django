from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import signals

from ..common import models as common_models
from ..filament import models as filament_models
from ..user_profile import models as user_profile_models

from ...libs import models as libs_models, signals as libs_signals, storage_backends


class PrintOrder(libs_models.SoftDeleteModel):

    # ! IMPORTANT ! For every change in server side (django choices) adjust frontend enums (constants.vue)

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

    user_profile = models.ForeignKey(user_profile_models.UserProfile, null=True, on_delete=models.SET_NULL)

    contact_email = models.EmailField()
    shipping_address = models.ForeignKey(common_models.ShippingAddress, on_delete=models.RESTRICT)
    billing_address = models.ForeignKey(common_models.BillingAddress, on_delete=models.RESTRICT)
    shipping_method = models.ForeignKey(common_models.ShippingMethod, null=True, on_delete=models.SET_NULL)
    # TODO add payment method

    comment = models.TextField(blank=True, null=True)

    # Images and PDFs
    attachment_files = GenericRelation(common_models.AttachmentFile)
    attachment_images = GenericRelation(common_models.AttachmentImage)

    estimated_price = models.DecimalField(max_digits=12, decimal_places=2)
    estimated_time = models.PositiveIntegerField()

    status = models.CharField(max_length=16, choices=ORDER_STATUS_CHOICES, default='awaiting_payment')
    
    def __str__(self):
        return "{}: [{}] BY={} CONTACT_EMAIL={} STATUS={}".format(self.pk, self.created_at, self.user_profile.user.email if self.user_profile is not None and self.user_profile.user is not None else 'guest', self.contact_email, self.status )


class OrderUnit(libs_models.SoftDeleteModel):

    LENGTH_UNIT_CHOICES = {
        'inches': 'inches',
        'mms': 'mms'
    }

    comment = models.TextField(blank=True, null=True)

    spool = models.ForeignKey(filament_models.Spool, on_delete=models.CASCADE)
    infill = models.ForeignKey(filament_models.Infill, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()

    file = models.FileField(storage=storage_backends.PrivateMediaStorage(), upload_to='print_order_files')

    attachment_files = GenericRelation(common_models.AttachmentFile)
    attachment_images = GenericRelation(common_models.AttachmentImage)

    length_unit = models.CharField(max_length=8)

    order = models.ForeignKey(PrintOrder, on_delete=models.CASCADE)

    estimated_price = models.DecimalField(max_digits=12, decimal_places=2)
    estimated_time = models.PositiveIntegerField()

    model_volume = models.FloatField(help_text='Volume with length_unit unit. Format: "x,y,z"')
    model_dimensions = models.CharField(max_length=128, help_text='Dimensions with length_unit unit.')

    model_rotation = models.CharField(max_length=128, help_text='Rotation chosen by user on frontend. Format: "x,y,z"')
    optimal_rotation = models.CharField(max_length=128, help_text='Rotation determined by Threejs on frontend to be optimal. Format: "x,y,z"')
    use_optimal_rotation = models.BooleanField(help_text='If true then optimal_rotation should bu used, else use model_rotation')

    length_unit = models.CharField(max_length=8, help_text='mms or inches')
    rotation_unit = models.CharField(max_length=12, help_text="degrees or radians")

    def __str__(self):
        return "{}: [{}] {} ATTRIBUTES={},{}".format(self.pk, self.created_at, self.file, self.spool, self.length_unit)


signals.pre_save.connect(receiver=libs_signals.send_email_on_order_status_change, sender=PrintOrder)