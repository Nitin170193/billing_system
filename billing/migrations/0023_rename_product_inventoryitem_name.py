# Generated by Django 5.1.6 on 2025-03-06 03:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0022_remove_invoice_discount_percentage'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inventoryitem',
            old_name='product',
            new_name='name',
        ),
    ]
