# Generated by Django 5.0 on 2024-04-28 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Order', '0006_rename_payed_order_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='per_item_price',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),
    ]
