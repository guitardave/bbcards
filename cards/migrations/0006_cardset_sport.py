# Generated by Django 4.2.16 on 2024-09-26 01:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0005_cardlistexport'),
    ]

    operations = [
        migrations.AddField(
            model_name='cardset',
            name='sport',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
