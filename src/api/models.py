from django.db import models
from django.core.validators import MaxValueValidator

# Create your models here.


class Project(models.Model):
    name = models.CharField(max_length=32, blank=False)
    url = models.CharField(max_length=255, blank=False)
    image = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name.lower()

    def lower(self):
        return self.name.lower()

class Port(models.Model):
    project = models.ForeignKey(Project, related_name='ports', on_delete=models.CASCADE)
    number = models.PositiveIntegerField(MaxValueValidator(65535))

    def __str__(self):
        return self.number

class Volume(models.Model):
    project = models.ForeignKey(Project, related_name='volumes', on_delete=models.CASCADE)
    path = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return self.path
