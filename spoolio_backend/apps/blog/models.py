from django.contrib.auth import get_user_model
from django.db import models

from ...apps.authentication import models as auth_models
from ...libs import models as common_models


class Blog(common_models.SoftDeleteModel):

    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    title = models.CharField(max_length=256)
    content = models.TextField()
    
    def __str__(self):
        return "{}: {}".format(self.author.username, self.title)