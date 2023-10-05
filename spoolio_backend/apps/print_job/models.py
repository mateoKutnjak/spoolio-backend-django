from django.db import models

from .. print_order import models as print_order_models
from .. printer import models as printer_models

from ... libs import models as libs_models


class PrintingJob(libs_models.BaseTimestampModel):

    STATUS_REJECTED = 'rejected'
    STATUS_IN_CHECKOUT = 'in_checkout'
    STATUS_REVIEWING = 'reviewing'
    STATUS_IN_QUEUE = 'in_queue'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_DONE = 'done'

    PRINT_JOB_STATUS_CHOICES = [(item, item.replace('_', ' ').capitalize()) for item in [
        STATUS_REJECTED,
        STATUS_IN_CHECKOUT,
        STATUS_REVIEWING, 
        STATUS_IN_QUEUE, 
        STATUS_IN_PROGRESS, 
        STATUS_DONE,
    ]]

    print_order_unit = models.ForeignKey(print_order_models.OrderUnit, on_delete=models.CASCADE, blank=True, null=True, default=None)
    printer = models.ForeignKey(printer_models.Printer, on_delete=models.CASCADE)

    duration = models.PositiveIntegerField(help_text="Duration of printing job in seconds")

    start_at = models.DateTimeField(null=False, blank=False)
    end_at = models.DateTimeField(null=False, blank=False)

    status = models.CharField(max_length=16, choices=PRINT_JOB_STATUS_CHOICES, default=STATUS_IN_CHECKOUT)

    def __str__(self):
        if self.print_order_unit:
            return "{}: [Order #{}, Unit #{}, Status: {}] on {}".format(self.pk, self.print_order_unit.order.id, self.print_order_unit.pk, self.status, self.printer.name)
        else:
            return "{}: [Status: {}] on {}".format(self.pk, self.status, self.printer.name)
