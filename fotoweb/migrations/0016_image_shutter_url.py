# Generated by Django 3.2.10 on 2022-02-10 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fotoweb', '0015_image_private'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='shutter_url',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='shutter_url'),
        ),
    ]
