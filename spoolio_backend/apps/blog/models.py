from django.contrib.auth import get_user_model
from django.db import models

from ...libs import models as common_models


class Blog(common_models.SoftDeleteModel):

    BLOG_CATEGORY_CHOICES = (
        ('3d-printing', '3D Printing'),
        ('electronics', 'Electronics'),
        ('design', 'Design'),
    )

    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    title = models.CharField(max_length=256)
    subtitle = models.CharField(max_length=1024)

    content = models.TextField()

    picture = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    
    type = models.CharField(max_length=16, choices=BLOG_CATEGORY_CHOICES)

    def __str__(self):
        return "{}: {}".format(self.author.username, self.title)