# Generated by Django 4.2.16 on 2024-09-13 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0002_player_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='slug',
            field=models.SlugField(unique=True),
        ),
    ]
