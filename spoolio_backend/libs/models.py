from django.db import models as models


class SoftDeleteManager(models.Manager):
    """
    TODO add docs
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteModel(models.Model):
    """
    TODO add docs
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    # ? This one should be defined FIRST because that way admin will use it
    objectsWithDeleted = models.Manager()

    # ? Override Model.objects.all() call to exclude deleted objects ('is_deleted' = True)
    objects = SoftDeleteManager()

    def save(self, *args, **kwargs):

        # ? Needed because signals.py does not receive update_fields list

        if self.pk:
            # If self.pk is not None then it's an update.

            cls = self.__class__
            old = cls.objectsWithDeleted.get(pk=self.pk)    # ? So we can restore or update models with 'is_deleted'

            # This will get the current model state since super().save() isn't called yet.
            new = self  # This gets the newly instantiated Mode object with the new values.
            changed_fields = ['updated_at']
            for field in cls._meta.get_fields():
                field_name = field.name
                try:
                    if getattr(old, field_name) != getattr(new, field_name):
                        changed_fields.append(field_name)
                except Exception as ex:  # Catch field does not exist exception
                    pass
            kwargs['update_fields'] = changed_fields
        print(kwargs.get('update_fields', []))
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True

        # * NOTE updated_at added because otherwise it wont get updated
        self.save(update_fields=['is_deleted', 'updated_at'])

    class Meta:
        abstract = True

    def __str__(self):
        return "{}{}: ".format("DELETED" if self.is_deleted else "", self.pk)