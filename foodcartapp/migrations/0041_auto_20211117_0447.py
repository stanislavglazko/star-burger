# Generated by Django 3.2 on 2021-11-17 04:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_remove_order_comments'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='customer_address',
            new_name='address',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='customer_name',
            new_name='firstname',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='customer_last_name',
            new_name='lastname',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='customer_phone_number',
            new_name='phonenumber',
        ),
    ]
