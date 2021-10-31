# Generated by Django 3.2.6 on 2021-09-22 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0002_card_card_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='cardset',
            name='slug',
            field=models.SlugField(null=True),
        ),
        migrations.AlterField(
            model_name='card',
            name='card_image',
            field=models.FileField(blank=True, default=None, null=True, upload_to='upload/'),
        ),
        migrations.AlterField(
            model_name='cardset',
            name='card_set_name',
            field=models.CharField(default=None, max_length=45),
        ),
    ]