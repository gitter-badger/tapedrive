# Generated by Django 2.0 on 2018-05-09 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='podcast',
            name='fetched',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Feed Fetched Last'),
        ),
    ]
