# Generated by Django 3.2 on 2021-11-26 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0052_auto_20211126_0419'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='restaurant',
            field=models.ManyToManyField(blank=True, related_name='orders', to='foodcartapp.Restaurant', verbose_name='Рестораны'),
        ),
    ]