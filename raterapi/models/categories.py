from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    label = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.label

    class Meta:
        verbose_name_plural = "categories"
