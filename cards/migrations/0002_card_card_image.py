# Generated by Django 3.2.6 on 2021-09-22 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='card_image',
            field=models.FileField(default=None, null=True, upload_to='upload/'),
        ),
    ]
