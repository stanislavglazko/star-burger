# Generated by Django 3.2 on 2021-11-15 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0038_order_orderitem'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'verbose_name': 'Заказ', 'verbose_name_plural': 'Заказы'},
        ),
        migrations.AddField(
            model_name='order',
            name='comments',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Комменты'),
        ),
    ]