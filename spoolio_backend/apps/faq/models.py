from django.db import models

from ...libs import models as libs_models, storage_backends


class Category(models.Model):

    name = models.CharField(max_length=128)
    description = models.CharField(max_length=256)

    picture = models.ImageField(storage=storage_backends.PublicMediaStorage(), upload_to='faq_blog_images/', null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class Blog(libs_models.BaseTimestampModel):

    title = models.CharField(max_length=256)
    subtitle = models.CharField(max_length=1024)

    content = models.TextField()

    picture = models.ImageField(storage=storage_backends.PublicMediaStorage(), upload_to='faq_blog_images/', null=True, blank=True)
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return "{}: [{}]: {}".format(self.pk, self.category.name, self.title)
