from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import models


@receiver(post_save, sender=get_user_model(), weak=False)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        models.UserProfile.objects.create(user=instance)