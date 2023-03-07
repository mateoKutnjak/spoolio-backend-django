from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from django.db import models

from ...libs import models as libs_models, storage_backends


class Like(libs_models.SoftDeleteModel):

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "content_type", "object_id"], 
                condition=models.Q(is_deleted=False), 
                name='like_unique_undeleted')
        ]

    def __str__(self):
        return "{}: [{}] {} (CONTENT_TYPE={}, OBJECT_ID={})".format(self.pk, self.created_at, self.user.email, self.content_type, self.object_id)


class Comment(libs_models.SoftDeleteModel):

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    content = models.TextField()

    likes = GenericRelation(Like)

    def __str__(self):
        return "{}: [{}] {} (CONTENT_TYPE={}, OBJECT_ID={})".format(self.pk, self.created_at, self.user.email, self.content_type, self.object_id)


class Rating(libs_models.SoftDeleteModel):

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    value = models.IntegerField(validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ])
    
    content = models.TextField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "content_type", "object_id"], 
                condition=models.Q(is_deleted=False), 
                name='rating_unique_undeleted')
        ]

    def __str__(self):
        return "{}: [{}] {} (CONTENT_TYPE={}, OBJECT_ID={}) VALUE={}".format(self.pk, self.created_at, self.user.email, self.content_type, self.object_id, self.value)


class ShippingAddress(libs_models.SoftDeleteModel):

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
        return "[{} {}] {}, {} {}, {}".format(self.first_name, self. last_name, self.address, self.locality, self.postal_code, self.country) 


class BillingAddress(libs_models.SoftDeleteModel):

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
        return "[{} {}] {}, {} {}, {}".format(self.first_name, self. last_name, self.address, self.locality, self.postal_code, self.country) 


class AttachmentFile(libs_models.SoftDeleteModel):

    file = models.FileField(storage=storage_backends.PrivateMediaStorage(), upload_to='attachment-files/')
    comment = models.TextField(blank=True, null=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self):
        return "{}: [{}] {} (CONTENT_TYPE={}, OBJECT_ID={}) has_comment={}".format(self.pk, self.created_at, self.file, self.content_type, self.object_id, bool(self.comment))


class AttachmentImage(libs_models.SoftDeleteModel):

    image = models.ImageField(storage=storage_backends.PrivateMediaStorage(), upload_to='attachment-images/')
    comment = models.TextField(blank=True, null=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self):
        return "{}: [{}] {} (CONTENT_TYPE={}, OBJECT_ID={}) has_comment={}".format(self.pk, self.created_at, self.image, self.content_type, self.object_id, bool(self.comment))


class ShippingMethod(libs_models.SoftDeleteModel):

    provider = models.CharField(max_length=64)
    description = models.CharField(max_length=128)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    available = models.BooleanField()

    def __str__(self) -> str:
        return "{}: {} (${})".format(self.pk, self.provider, self.price)