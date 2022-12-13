from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from ...libs import models as libs_models


class Like(models.Model):

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        unique_together = (("user", "content_type", "object_id"),)

    def __str__(self):
        return super(Like, self).__str__() + "by {}, {}: {}".format(self.user, self.content_type, self.content_object)


class Comment(libs_models.SoftDeleteModel):

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    content = models.TextField()

    likes = GenericRelation(Like)

    def __str__(self):
        return "{} COMMENT ON {} with ID={}".format(self.user.email, self.content_type, self.object_id)
