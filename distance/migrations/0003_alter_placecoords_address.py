# Generated by Django 3.2 on 2021-12-03 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distance', '0002_auto_20211203_0545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='placecoords',
            name='address',
            field=models.CharField(max_length=100, unique=True, verbose_name='Адрес места'),
        ),
    ]