from django.contrib.auth import get_user_model
from django.db import models

from ...libs import models as libs_models


class InvitationToken(libs_models.SoftDeleteModel):

    value = models.CharField(max_length=32)
    user = models.OneToOneField(get_user_model(), null=True, blank=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return "{}: USER={}".format(self.value, self.user.email if self.user else 'null')