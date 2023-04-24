from datetime import datetime, timedelta

from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import signals
from django.dispatch import receiver
import logging

from ..common import models as common_models
from ..filament import models as filament_models
from ..print_job import models as print_job_models
from ..printer import models as printer_models
from ..user_profile import models as user_profile_models

from ...libs import models as libs_models, signals as libs_signals, storage_backends


logger = logging.getLogger(__name__)


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


class OrderUnit(libs_models.BaseTimestampModel):

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

    screenshot = models.ImageField(storage=storage_backends.PrivateMediaStorage(), upload_to='print_unit_screenshots/', null=True, blank=True)

    def __str__(self):
        return "{}: [{}] {} ATTRIBUTES={},{}".format(self.pk, self.created_at, self.file, self.spool, self.length_unit)


# * Every time 'status' field of PrintOrder changes, send email to 'contact_email' field
signals.pre_save.connect(receiver=libs_signals.send_email_on_order_status_change, sender=PrintOrder)

def create_printing_job_for_print_order_unit(sender, instance, created, **kwargs):

    # ! STATUS_IN_PROGRESS means that printing order has been 
    # ! paid and has to be printed and sent to customer

    # ! This can cause problems in future. 

    if instance.status != PrintOrder.STATUS_IN_PROGRESS:
        return

    START_WORKING_TIME_HOURS = 7
    START_WORKING_TIME_MINUTES = 0
    END_WORKING_TIME_HOURS = 15
    END_WORKING_TIME_MINUTES = 0

    BUFFER_AFTER_HOURS = 1
    BUFFER_AFTER_MINUTES = 0

    BUFFER_AFTER = timedelta(hours=BUFFER_AFTER_HOURS, minutes=BUFFER_AFTER_MINUTES)

    logger.info('Order #{} has been paid. Creating printer jobs for every unit.'.format(instance.pk))
    logger.info('   Working day (UTC time): FROM {:02d}:{:02d} TO {:02d}:{:02d}'.format(START_WORKING_TIME_HOURS, START_WORKING_TIME_MINUTES, END_WORKING_TIME_HOURS, END_WORKING_TIME_MINUTES))
    logger.info('   Time buffer after previous job is finished: {:02d}:{:02d}'.format(BUFFER_AFTER_HOURS, BUFFER_AFTER_MINUTES))

    print_order_units = OrderUnit.objects.filter(order=instance.id)

    logger.info('')
    logger.info('   Number of print units: {}'.format(len(print_order_units)))

    for unit in print_order_units:

        logger.info('')
        logger.info('   Unit #{} [material={}]'.format(unit.pk, unit.spool.material.name))

        last_printer_jobs = []
        printers = printer_models.Printer.objects.filter(available=True, type__supported_materials__in=[unit.spool.material])
        logger.info('   {} printers found that work with material={}'.format(len(printers), unit.spool.material.name))
        
        if not printers:
            return

        for printer in printers:

            # * Fetch newest printing job on priter with status 'in_queue' or 'in_progress'
            # *
            # * filter leaves only printing orders with 'in_queue' and 'in_progress' status
            # * order_by('end_at') orders printing jobs from oldest to newest
            # * last() fetches newest printing job or None if list is empty
            last_printer_job = print_job_models.PrintingJob.objects.filter(printer=printer, status__in=[print_job_models.PrintingJob.STATUS_IN_QUEUE, print_job_models.PrintingJob.STATUS_IN_PROGRESS]).order_by('end_at').last()
            
            if last_printer_job:
                logger.info('   Printer {} has last job #{} which ends at {}'.format(printer.name, last_printer_job.pk, last_printer_job.end_at))
            else:
                logger.info('   Printer {} has no "in_queue" or "in_progress" jobs'.format(printer.name))

            last_printer_jobs.append((last_printer_job, printer))

        # * Sort last job of every printer based on time it ends. Put empty printers with 
        # * last job == None at the beginning of the sorted list to be fetched first
        last_printer_jobs_sorted = sorted(last_printer_jobs, key=lambda item: (item[0] is not None and item[0].end_at is not None, item[0].end_at))

        # * Fetch printer job that ends first
        job_previous = last_printer_jobs_sorted[0][0] if len(last_printer_jobs_sorted) > 0 else None
        printer = last_printer_jobs_sorted[0][1] if len(last_printer_jobs_sorted) > 0 else None

        logger.info('')

        # * Determine end time of previous job to which new jobe will be appended
        if job_previous is None:
            # * Printer does not have any 'in_queue' or 'in_progress' jobs so current time
            # * is used as a 'dummy' printing job end time to indicate that printer has
            # * just finished his last job and can be used immediately (with taking weekends 
            # * into consideration)

            now = datetime.now()

            if now.isoweekday() in [1,2,3,4,5]:
                # ? Mon, Tue, Wed, Thu, Sun - add one day
                days_to_add = 0
            elif now.isoweekday() == 6:
                # ? Fri - add three days
                days_to_add = 2
            elif now.isoweekday() == 7:
                # ? Sat - add two days
                days_to_add = 1

            end_at_previous = datetime.now() + timedelta(days=days_to_add)

            logger.info('   Printer {} is available immediatelly (has no active printing jobs)'.format(printer.name))
            logger.info('   Because today weekday number is {}, we will add {} days.\n'.format(end_at_previous.isoweekday(), days_to_add))

        else:
            # * Printer has jobs in his job queue so last job ending time is used (if it
            # * in future). If last printing job ending is not in the future, use current
            # * time as last job ending time.

            now = datetime.now()

            if job_previous.end_at.timestamp() < now.timestamp():
                end_at_previous = now
            else:                
                end_at_previous = datetime.fromtimestamp(job_previous.end_at.timestamp())

            # ! This should not be on weekends or holiday 
            # ! and algorith below forbids that situation

            logger.info('   Printer {} will be available first at {} when job #{} ends'.format(printer.name, last_printer_job.end_at, last_printer_job.pk))

        # * Determine if job ends after working time
        working_day_start = end_at_previous.replace(hour=START_WORKING_TIME_HOURS, minute=START_WORKING_TIME_MINUTES, second=0)
        working_time_end = end_at_previous.replace(hour=END_WORKING_TIME_HOURS, minute=END_WORKING_TIME_MINUTES, second=0)

        if end_at_previous > working_day_start and end_at_previous < working_time_end:
            # * Job is done in middle of the working day. 
            logger.info('   Last job is done at {:02d}:{:02d}:{:02d} which is middle of working day ({:02d}:{:02d} - {:02d}:{:02d})'.format(end_at_previous.hour, end_at_previous.minute, end_at_previous.second, START_WORKING_TIME_HOURS, START_WORKING_TIME_MINUTES, END_WORKING_TIME_HOURS, END_WORKING_TIME_MINUTES))

            if end_at_previous + BUFFER_AFTER < working_time_end:
                logger.info('   Even considering time buffer, new job can be placed today')
                # * Job is done before end of the work day with BUFFER_AFTER taken into consideration.
                # * Add new job after this one in the same day

                start_at = end_at_previous + BUFFER_AFTER
                end_at = start_at + timedelta(seconds=unit.estimated_time)

            else:
                # * When taking BUFFER_AFTER into consideration, job ends after working hours, so
                # * it is shifted for next working day
                logger.info('   Considering time buffer, new job cannot be placed today')

                # * Determine how much days to add for every possible weekday when job ends
                if end_at_previous.isoweekday() in [1,2,3,4,7]:
                    # ? Mon, Tue, Wed, Thu, Sun - add one day
                    days_to_add = 1
                elif end_at_previous.isoweekday() == 5:
                    # ? Fri - add three days
                    days_to_add = 3
                elif end_at_previous.isoweekday() == 6:
                    # ? Sat - add two days
                    days_to_add = 2

                logger.info('   Because today weekday number is {}, we will add {} days.\n'.format(end_at_previous.isoweekday(), days_to_add))

                start_at = end_at_previous + timedelta(days=days_to_add)
                start_at = start_at.replace(hour=START_WORKING_TIME_HOURS, minute=START_WORKING_TIME_MINUTES)

        elif end_at_previous < working_day_start:

            # * Job is done before working day starts so it is placed in the same day
            # * right when working hours start

            logger.info('   Last job is done at {:02d}:{:02d}:{:02d} which is before working day starts ({:02d}:{:02d} - {:02d}:{:02d})'.format(end_at_previous.hour, end_at_previous.minute, end_at_previous.second, START_WORKING_TIME_HOURS, START_WORKING_TIME_MINUTES, END_WORKING_TIME_HOURS, END_WORKING_TIME_MINUTES))

            start_at = end_at_previous.replace(hour=START_WORKING_TIME_HOURS, minute=START_WORKING_TIME_MINUTES)

        elif end_at_previous > working_time_end:

            # * Job is done after working day ends so it is placed in the next working day
            # * right when working hours start

            logger.info('   Last job is done at {:02d}:{:02d}:{:02d} which is after working day ends ({:02d}:{:02d} - {:02d}:{:02d})'.format(end_at_previous.hour, end_at_previous.minute, end_at_previous.second, START_WORKING_TIME_HOURS, START_WORKING_TIME_MINUTES, END_WORKING_TIME_HOURS, END_WORKING_TIME_MINUTES))

            if end_at_previous.isoweekday() in [1,2,3,4,7]:
                # ? Mon, Tue, Wed, Thu, Sun - add one day
                days_to_add = 1
            elif end_at_previous.isoweekday() == 5:
                # ? Fri - add three days
                days_to_add = 3
            elif end_at_previous.isoweekday() == 6:
                # ? Sat - add two days
                days_to_add = 2

            start_at = end_at_previous + timedelta(days=days_to_add)
            start_at = start_at.replace(hour=START_WORKING_TIME_HOURS, minute=START_WORKING_TIME_MINUTES)

        else:
            logger.error('Cannot create printing job for OrderUnit #{}. Cannot determine previous job ending time placement in working day'.format(unit.id))
            return

        end_at = start_at + timedelta(seconds=unit.estimated_time)

        # * Default status is 'in_queue'.
        job = print_job_models.PrintingJob.objects.create(
            print_order_unit=unit, 
            printer=printer,
            duration=instance.estimated_time,
            start_at=start_at,
            end_at=end_at)
        
        logger.info('')
        logger.info('Printing job #{} created for print order unit #{} on printer {}'.format(job.id, instance.id, printer.name))
        logger.info('   Printing starts at: {}'.format(job.start_at))
        logger.info('   Printing starts at: {}'.format(job.end_at))

# * Every time new OrderUnit is added, create PrintingJob (app print_job)
# ! Signal will not be called with .update() method on queryset.
# ! It will be called with .save() method on model object
# !
# ! See how status gets updated in 'payment/views.py'
signals.post_save.connect(receiver=create_printing_job_for_print_order_unit, sender=PrintOrder)
