from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from ..common import models as common_models

from ...libs import models as libs_models, storage_backends


class Category(models.Model):

    name = models.CharField(max_length=128)

    def __str__(self) -> str:
        return self.name


class Subcategory(models.Model):

    name = models.CharField(max_length=128)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return "{} [category={}]".format(self.name, self.category)


class Tag(models.Model):

    name = models.CharField(max_length=128)

    def __str__(self) -> str:
        return self.name


class Blog(libs_models.SoftDeleteModel):

    author = author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    title = models.CharField(max_length=256)
    subtitle = models.CharField(max_length=1024)

    content = models.TextField()

    picture = models.ImageField(storage=storage_backends.PublicMediaStorage(), upload_to='blog_images/', null=True, blank=True)
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    is_featured = models.BooleanField(default=False)

    comments = GenericRelation(common_models.Comment)
    likes = GenericRelation(common_models.Like)

    def __str__(self):
        return "{}: {} [{}] AUTHOR={}: {}".format(self.pk, '[FEATURED]' if self.is_featured else '', self.category.id, self.author.username, self.title)
