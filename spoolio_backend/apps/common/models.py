from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from django.db import models

from ...libs import models as libs_models, storage_backends


class Like(models.Model):

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "content_type", "object_id"], 
                name='like_unique')
        ]

    def __str__(self):
        return "{}: [{}] (CONTENT_TYPE={}, OBJECT_ID={})".format(self.pk, self.user.email, self.content_type, self.object_id)


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

    TYPE_INDIVIDUAL = 'individual'
    TYPE_COMPANY = 'company'

    CHOICES_TYPE = (
        (TYPE_INDIVIDUAL, TYPE_INDIVIDUAL.capitalize()),
        (TYPE_COMPANY, TYPE_COMPANY.capitalize()),
    )

    type = models.CharField(max_length=16, choices=CHOICES_TYPE)

    first_name = models.CharField(max_length=64, null=True, blank=True)
    last_name = models.CharField(max_length=64, null=True, blank=True)
    address = models.CharField(max_length=256)
    state = models.CharField(max_length=128, null=True, blank=True)
    country = models.CharField(max_length=128)
    locality = models.CharField(max_length=128)
    postal_code = models.IntegerField()

    phone_regex = RegexValidator(regex=r'^\+\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    vat_id_regex = RegexValidator(regex=r'^((AT)?U[0-9]{8}|(BE)?0[0-9]{9}|(BG)?[0-9]{9,10}|(HR)?[0-9]{11}|(CY)?[0-9]{8}L|(CZ)?[0-9]{8,10}|(DE)?[0-9]{9}|(DK)?[0-9]{8}|(EE)?[0-9]{9}|(EL|GR)?[0-9]{9}|ES[A-Z][0-9]{7}(?:[0-9]|[A-Z])|(FI)?[0-9]{8}|(FR)?[0-9A-Z]{2}[0-9]{9}|(GB)?([0-9]{9}([0-9]{3})?|[A-Z]{2}[0-9]{3})|(HU)?[0-9]{8}|(IE)?[0-9]S[0-9]{5}L|(IT)?[0-9]{11}|(LT)?([0-9]{9}|[0-9]{12})|(LU)?[0-9]{8}|(LV)?[0-9]{11}|(MT)?[0-9]{8}|(NL)?[0-9]{9}B[0-9]{2}|(PL)?[0-9]{10}|(PT)?[0-9]{9}|(RO)?[0-9]{2,10}|(SE)?[0-9]{12}|(SI)?[0-9]{8}|(SK)?[0-9]{10})$', message="VAT ID is not valid accourding to regular expression rules")

    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True) # Validators should be a list

    contact_first_name = models.CharField(max_length=64, null=True, blank=True)
    contact_last_name = models.CharField(max_length=64, null=True, blank=True)
    company_name = models.CharField(max_length=256, null=True, blank=True)
    vat_id = models.CharField(validators=[vat_id_regex], max_length=20, blank=True)

    def __str__(self) -> str:
        if self.type == self.TYPE_INDIVIDUAL:
            return "{} [{} {}] {}, {} {}, {}".format(self.type, self.first_name, self.last_name, self.address, self.locality, self.postal_code, self.country) 
        elif self.type == self.TYPE_COMPANY:
            return "{} [{}] {}, {} {}, {}".format(self.type, self.company_name, self.address, self.locality, self.postal_code, self.country) 
        return 'Unknown type. Fix __str__ for model'


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