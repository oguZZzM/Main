# Generated by Django 5.2 on 2025-04-21 16:18

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('siparis', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='musteri',
            name='kayit_tarihi',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
