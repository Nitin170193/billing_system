# Generated by Django 5.1.6 on 2025-03-02 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0017_invoice_gst_invoice_price_invoice_product_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='gst',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='price',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='product',
        ),
        migrations.AddField(
            model_name='invoiceitem',
            name='gst',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='invoiceitem',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='invoiceitem',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
