# Generated by Django 2.0.1 on 2018-02-12 23:08

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('url', models.CharField(max_length=255)),
                ('port', models.PositiveIntegerField(verbose_name=django.core.validators.MaxValueValidator(65535))),
            ],
        ),
    ]
