# Generated by Django 5.1.6 on 2025-03-08 05:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0041_alter_regitration_admin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='regitration',
            name='admin',
        ),
    ]
