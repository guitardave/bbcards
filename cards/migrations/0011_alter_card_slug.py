# Generated by Django 4.2.16 on 2024-10-27 00:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0010_card_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='slug',
            field=models.SlugField(max_length=250, null=True, unique=True),
        ),
    ]
