# Generated by Django 3.2.7 on 2021-11-21 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fotoweb', '0007_album_cover'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='cover',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='cover'),
        ),
    ]
