# Generated by Django 5.1.6 on 2025-03-08 09:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0052_invoice_user_invoiceitem_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='user',
        ),
        migrations.RemoveField(
            model_name='invoiceitem',
            name='user',
        ),
    ]
