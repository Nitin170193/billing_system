# Generated by Django 5.1.6 on 2025-03-02 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0011_invoice_payable_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='paid_amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True),
        ),
    ]
