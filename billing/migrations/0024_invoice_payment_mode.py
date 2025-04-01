# Generated by Django 5.1.6 on 2025-03-06 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0023_rename_product_inventoryitem_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='payment_mode',
            field=models.CharField(choices=[('Cash', 'Cash'), ('Card', 'Card'), ('UPI', 'UPI'), ('Net Banking', 'Net Banking')], default='Cash', max_length=20),
        ),
    ]
