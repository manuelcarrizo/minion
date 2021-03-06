from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class Project(models.Model):
    name = models.CharField(max_length=32, blank=False)
    url = models.CharField(max_length=255, blank=False)
    image = models.CharField(max_length=255, blank=False, default='')

    def __str__(self):
        return self.name.lower()

    def lower(self):
        return self.name.lower()

PROTOCOL_CHOICES = (
    ('tcp', 'tcp'),
    ('udp', 'udp')
)

class Port(models.Model):
    project = models.ForeignKey(Project, related_name='ports', on_delete=models.CASCADE)
    host = models.PositiveIntegerField(MaxValueValidator(65535), primary_key=True)
    container = models.PositiveIntegerField(MaxValueValidator(65535))
    protocol = models.CharField(max_length=3, choices=PROTOCOL_CHOICES, default='tcp')

    def __str__(self):
        return "%d/%s" % (self.container, self.protocol)

class Volume(models.Model):
    project = models.ForeignKey(Project, related_name='volumes', on_delete=models.CASCADE)
    path = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return self.path

class EnvVar(models.Model):
    project = models.ForeignKey(Project, related_name='envvars', on_delete=models.CASCADE)
    key = models.CharField(max_length=255, blank=False)
    value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return "%s=%s" % (self.key, self.value)
