# Generated by Django 4.2.16 on 2024-10-28 17:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0012_card_uu_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='card',
            name='uu_id',
        ),
    ]
