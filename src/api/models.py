from django.db import models
from django.core.validators import MaxValueValidator

# Create your models here.


class Project(models.Model):
    name = models.CharField(max_length=32, blank=False)
    url = models.CharField(max_length=255, blank=False)
    port = models.PositiveIntegerField(MaxValueValidator(65535))
