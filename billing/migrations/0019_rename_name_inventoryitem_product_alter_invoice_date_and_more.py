# Generated by Django 5.1.6 on 2025-03-05 04:56

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0018_remove_invoice_gst_remove_invoice_price_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inventoryitem',
            old_name='name',
            new_name='product',
        ),
        migrations.AlterField(
            model_name='invoice',
            name='date',
            field=models.DateField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='discount_percentage',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=5, null=True),
        ),
    ]
