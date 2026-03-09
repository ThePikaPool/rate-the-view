from django.db import models
from django.contrib.auth.models import User


class View(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=128)
    description = models.CharField(max_length=256)
    view_count = models.IntegerField(default=0)

    def __str__(self):
        return self.location


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    view = models.ForeignKey(View, on_delete=models.CASCADE)
    content = models.CharField(max_length=256)

    def __str__(self):
        return self.content


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    view = models.ForeignKey(View, on_delete=models.CASCADE)
    upvote = models.BooleanField(default=False)
    downvote = models.BooleanField(default=False)