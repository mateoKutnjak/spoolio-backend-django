from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator
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


class ShippingAddress(models.Model):

    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    address = models.CharField(max_length=256)
    state = models.CharField(max_length=128, null=True, blank=True)
    country = models.CharField(max_length=128)
    locality = models.CharField(max_length=128)
    postal_code = models.IntegerField()

    phone_regex = RegexValidator(regex=r'^\+\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True) # Validators should be a list

    def __str__(self) -> str:
        return "{} ... {} ... [{}]".format(self.address, self.postal_code, self.country) 


class BillingAddress(models.Model):

    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    address = models.CharField(max_length=256)
    state = models.CharField(max_length=128, null=True, blank=True)
    country = models.CharField(max_length=128)
    locality = models.CharField(max_length=128)
    postal_code = models.IntegerField()

    phone_regex = RegexValidator(regex=r'^\+\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True) # Validators should be a list

    def __str__(self) -> str:
        return "{} ... {} ... [{}]".format(self.address, self.postal_code, self.country) 
