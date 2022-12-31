from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from .. common import models as common_models
from .. user_profile import models as user_profile_models

from ... libs import models as libs_models


class ModelingOrder(libs_models.SoftDeleteModel):

    user_profile = models.ForeignKey(user_profile_models.UserProfile, blank=True, null=True, on_delete=models.SET_NULL)

    contact_email = models.EmailField()
    comment = models.TextField(blank=True, null=True)

    # Images and PDFs
    attachment_files = GenericRelation(common_models.AttachmentFile)
    attachment_images = GenericRelation(common_models.AttachmentImage)

    def __str__(self):
        return "{}: [{}] BY={} CONTACT_EMAIL={}".format(self.pk, self.created_at, self.user_profile.email if self.user_profile is not None else 'guest', self.contact_email )

