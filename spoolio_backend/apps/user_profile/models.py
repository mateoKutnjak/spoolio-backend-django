from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):

    user = models.OneToOneField(get_user_model(), null=True, blank=True, on_delete=models.CASCADE)

    # * This should be used only when GUEST account is used (without user FK)
    # * If user FK is used, use its email field which is used for authentication
    email = models.EmailField(null=True, blank=True)

    first_name = models.CharField(max_length=64, null=True, blank=True)
    last_name = models.CharField(max_length=64, null=True, blank=True)

    address = models.CharField(max_length=256, null=True, blank=True)

    phone_regex = RegexValidator(regex=r'^\+\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True) # Validators should be a list


    def __str__(self) -> str:
        if self.user == None:
            return "[{}] {} [GUEST]".format(self.pk, self.email)
        return "[{}] {}".format(self.pk, self.user.email)


@receiver(post_save, sender=get_user_model())
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)