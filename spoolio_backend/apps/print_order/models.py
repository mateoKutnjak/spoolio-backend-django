from django.db import models

from ..user_profile import models as user_profile_models

from ...libs import models as common_models


class OrderAttachmentFile(models.Model):

    file = models.FileField(upload_to="order_attachment_files")


class PrintOrder(common_models.SoftDeleteModel):

    ORDER_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In progress'),
        ('completed', 'Completed'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
    )

    user_profile = models.ForeignKey(user_profile_models.UserProfile, on_delete=models.CASCADE)

    comment = models.TextField(blank=True, null=True)
    attachments = models.ManyToManyField(OrderAttachmentFile, blank=True)

    status = models.CharField(max_length=16, choices=ORDER_STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return "[{}] print order by {}".format(self.status, self.user_profile.email)


