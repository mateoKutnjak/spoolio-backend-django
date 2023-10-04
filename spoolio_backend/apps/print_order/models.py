from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import signals

import logging

from ..common import models as common_models
from ..filament import models as filament_models
from ..print_job import tasks as print_job_tasks
from ..printer import models as printer_models
from ..user_profile import models as user_profile_models

from ...libs import models as libs_models, signals as libs_signals, storage_backends


logger = logging.getLogger(__name__)


class PrintUnitInfill(models.Model):
    name = models.CharField(max_length=16)
    percentage = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    available = models.BooleanField()

    def __str__(self) -> str:
        return "{} - {}%".format(self.name, self.percentage * 100)


class PrintUnitWall(models.Model):
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)])

    def __str__(self) -> str:
        return "{}".format(self.amount)


class PrintUnitWallThickness(models.Model):
    thickness = models.FloatField(validators=[MinValueValidator(
        0.0), MaxValueValidator(0.3)], help_text='In millimeters')

    def __str__(self) -> str:
        return "{}".format(self.thickness)


class PrintUnitInfillWallCombination(models.Model):

    name = models.CharField(max_length=128)
    infill = models.ForeignKey(PrintUnitInfill, on_delete=models.CASCADE)
    wall = models.ForeignKey(PrintUnitWall, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return "infill={}% [{}], walls={}".format(self.infill.percentage * 100, self.infill.name, self.wall.amount)


class CostVariables(models.Model):

    material_markup = models.FloatField(validators=[MinValueValidator(
        0.0), MaxValueValidator(10.0)], default=1.2, help_text='Cp (hint: 20% markup = 1.2)')
    print_hour_cost = models.FloatField(validators=[MinValueValidator(
        0.0), MaxValueValidator(10.0)], default=0.25, help_text='Ct (euros per hour)')
    post_process_cost = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(
        100.0)], default=2.0, help_text='Cpost (post processing cost per part)')
    price_margin = models.FloatField(validators=[MinValueValidator(
        0.0), MaxValueValidator(10.0)], default=3.0, help_text='Cm')
    prep_cost = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(
        100.0)], default=3.0, help_text='Cprep (total preperation cost)')

    def __str__(self) -> str:
        return "price = quantity x [quantity_multiplier x [{} x ({} x material + {} x time) + {}]] + {}".format(self.price_margin, self.material_markup, self.print_hour_cost, self.post_process_cost, self.prep_cost)


class QuantityMultiplier(models.Model):

    quantity_min = models.PositiveIntegerField(default=0)
    quantity_max = models.PositiveIntegerField(default=0)
    add_percentage = models.FloatField(validators=[MinValueValidator(
        0.0), MaxValueValidator(100.0)], default=1.2, help_text='Cq (hint: 20% markup = 1.2)')

    def __str__(self) -> str:
        return "From {} to {} pcs, {}%".format(self.quantity_min, self.quantity_max, round(100*self.add_percentage - 100, 2))


class PrintOrder(libs_models.BaseTimestampModel):

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

    user_profile = models.ForeignKey(
        user_profile_models.UserProfile, null=True, on_delete=models.SET_NULL)

    contact_email = models.EmailField()
    shipping_address = models.ForeignKey(
        common_models.ShippingAddress, on_delete=models.RESTRICT)
    billing_address = models.ForeignKey(
        common_models.BillingAddress, on_delete=models.RESTRICT)
    shipping_method = models.ForeignKey(
        common_models.ShippingMethod, null=True, on_delete=models.SET_NULL)
    # TODO add payment method

    comment = models.TextField(blank=True, null=True)

    # Images and PDFs
    attachment_files = GenericRelation(common_models.AttachmentFile)
    attachment_images = GenericRelation(common_models.AttachmentImage)

    estimated_price = models.DecimalField(max_digits=12, decimal_places=2)
    estimated_time = models.PositiveIntegerField()

    status = models.CharField(
        max_length=16, choices=ORDER_STATUS_CHOICES, default='awaiting_payment')

    def __str__(self):
        return "{}: [{}] BY={} CONTACT_EMAIL={} STATUS={}".format(self.pk, self.created_at, self.user_profile.user.email if self.user_profile is not None and self.user_profile.user is not None else 'guest', self.contact_email, self.status)


class OrderUnit(libs_models.BaseTimestampModel):

    LENGTH_UNIT_CHOICES = {
        'inches': 'inches',
        'mms': 'mms'
    }

    comment = models.TextField(blank=True, null=True)

    spool = models.ForeignKey(filament_models.Spool, on_delete=models.CASCADE)
    infill = models.ForeignKey(PrintUnitInfill, on_delete=models.CASCADE)
    wall = models.ForeignKey(PrintUnitWall, on_delete=models.CASCADE)
    wall_thickness = models.ForeignKey(
        PrintUnitWallThickness, on_delete=models.CASCADE)
    printing_method = models.ForeignKey(
        printer_models.PrintingMethod, on_delete=models.SET_NULL, null=True)

    scale = models.FloatField(validators=[
        MinValueValidator(0.001),
    ], default=1.0)

    quantity = models.PositiveIntegerField()

    file = models.FileField(
        storage=storage_backends.PrivateMediaStorage(), upload_to='print_order_files')

    attachment_files = GenericRelation(common_models.AttachmentFile)
    attachment_images = GenericRelation(common_models.AttachmentImage)

    length_unit = models.CharField(max_length=8)

    order = models.ForeignKey(PrintOrder, on_delete=models.CASCADE)

    estimated_price = models.DecimalField(max_digits=12, decimal_places=2)
    estimated_time = models.PositiveIntegerField()
    eta = models.DateTimeField(null=True, blank=True)

    model_volume = models.FloatField(
        help_text='Volume with length_unit unit. Format: "x,y,z"')
    model_dimensions = models.CharField(
        max_length=128, help_text='Dimensions with length_unit unit.')

    model_rotation = models.CharField(
        max_length=128, help_text='Rotation chosen by user on frontend. Format: "x,y,z"')
    optimal_rotation = models.CharField(
        max_length=128, help_text='Rotation determined by Threejs on frontend to be optimal. Format: "x,y,z"')
    use_optimal_rotation = models.BooleanField(
        help_text='If true then optimal_rotation should bu used, else use model_rotation')

    length_unit = models.CharField(max_length=8, help_text='mms or inches')
    rotation_unit = models.CharField(
        max_length=12, help_text="degrees or radians")

    screenshot = models.ImageField(storage=storage_backends.PrivateMediaStorage(
    ), upload_to='print_unit_screenshots/', null=True, blank=True)

    def __str__(self):
        return "{}: [{}] {} ATTRIBUTES={},{}".format(self.pk, self.created_at, self.file, self.spool, self.length_unit)


# * Every time 'status' field of PrintOrder changes, send email to 'contact_email' field
signals.pre_save.connect(
    receiver=libs_signals.print_order_pre_save_signal, sender=PrintOrder)
signals.post_save.connect(
    receiver=libs_signals.print_order_post_save_signal, sender=PrintOrder)


def create_printing_job_for_print_order_unit(sender, instance, created, raw, **kwargs):

    if raw:
        return

    # ! STATUS_IN_PROGRESS means that printing order has been
    # ! paid and has to be printed and sent to customer

    # ! This can cause problems in future.

    # if instance.status != PrintOrder.STATUS_IN_PROGRESS:
    #    return

    print_job_tasks.create_printing_jobs_for_print_order.delay({
        'data': {
            'print_order': {
                'id': instance.id,
                'status': instance.status,
            },
            'working_hours': {
                'start': {
                    'hours': settings.WORKING_HOURS_START_HOUR,
                    'minutes': settings.WORKING_HOURS_START_MINUTE,
                },
                'end': {
                    'hours': settings.WORKING_HOURS_END_HOUR,
                    'minutes': settings.WORKING_HOURS_END_MINUTE,
                },
            },
            'misc': {
                'buffer_after_print_job_done': {
                    'hours': settings.BUFFER_AFTER_PRINT_JOB_DONE_HOUR,
                    'minutes': settings.BUFFER_AFTER_PRINT_JOB_DONE_MINUTE,
                }
            }
        },
    })


# * Every time new OrderUnit is added, create PrintingJob (app print_job)
# ! Signal will not be called with .update() method on queryset.
# ! It will be called with .save() method on model object
# !
# ! See how status gets updated in 'payment/views.py'
signals.post_save.connect(
    receiver=create_printing_job_for_print_order_unit, sender=PrintOrder)
