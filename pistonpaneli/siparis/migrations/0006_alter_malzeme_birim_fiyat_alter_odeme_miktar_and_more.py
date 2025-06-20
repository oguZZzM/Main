# Generated by Django 5.2.3 on 2025-06-10 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('siparis', '0005_alter_malzeme_options_alter_malzemekullanimi_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='malzeme',
            name='birim_fiyat',
            field=models.IntegerField(default=0, help_text='Birim başına fiyat (TL)'),
        ),
        migrations.AlterField(
            model_name='odeme',
            name='miktar',
            field=models.IntegerField(help_text='Ödeme miktarı (TL)'),
        ),
        migrations.AlterField(
            model_name='rapor',
            name='toplam_gelir',
            field=models.IntegerField(default=0, help_text='Rapor dönemindeki toplam gelir (TL)'),
        ),
        migrations.AlterField(
            model_name='rapor',
            name='toplam_odenen',
            field=models.IntegerField(default=0, help_text='Rapor dönemindeki toplam tahsil edilen miktar (TL)'),
        ),
        migrations.AlterField(
            model_name='siparis',
            name='birim_fiyat',
            field=models.IntegerField(default=0, help_text='Birim fiyat (TL)'),
        ),
        migrations.AlterField(
            model_name='siparis',
            name='odenen_miktar',
            field=models.IntegerField(default=0, help_text='Ödenen miktar (TL)'),
        ),
        migrations.AlterField(
            model_name='siparis',
            name='toplam_fiyat',
            field=models.IntegerField(default=0, editable=False, help_text='Toplam fiyat (TL)'),
        ),
    ]
