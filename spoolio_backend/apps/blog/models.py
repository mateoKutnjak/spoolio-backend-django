from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from ..common import models as common_models

from ...libs import models as libs_models


class Blog(libs_models.SoftDeleteModel):

    BLOG_CATEGORY_CHOICES = (
        ('3d-printing', '3D Printing'),
        ('electronics', 'Electronics'),
        ('design', 'Design'),
    )

    author = author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    title = models.CharField(max_length=256)
    subtitle = models.CharField(max_length=1024)

    content = models.TextField()

    picture = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    
    type = models.CharField(max_length=16, choices=BLOG_CATEGORY_CHOICES)

    comments = GenericRelation(common_models.Comment)
    likes = GenericRelation(common_models.Like)

    def __str__(self):
        return "{}: [{}] AUTHOR={}: {}".format(self.pk, self.created_at, self.author.username, self.title)
