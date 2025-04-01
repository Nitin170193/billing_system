# Generated by Django 5.1.6 on 2025-03-02 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0015_alter_expense_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='payment_mode',
            field=models.CharField(choices=[('Cash', 'Cash'), ('UPI', 'UPI')], default='Cash', max_length=10),
        ),
        migrations.AlterField(
            model_name='expense',
            name='person_name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='expense',
            name='reference_person',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
