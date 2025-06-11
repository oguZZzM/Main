from django.core.management.base import BaseCommand
from siparis.models import Siparis, Odeme, Malzeme, Rapor
from django.db import transaction

class Command(BaseCommand):
    help = 'Convert existing decimal values to integers in the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting conversion of decimal values to integers...'))
        
        # Use transaction to ensure all or nothing
        with transaction.atomic():
            # Convert Siparis model fields
            self.stdout.write('Converting Siparis model fields...')
            for siparis in Siparis.objects.all():
                # Convert to integers by rounding
                siparis.birim_fiyat = int(round(siparis.birim_fiyat))
                siparis.toplam_fiyat = int(round(siparis.toplam_fiyat))
                # odenen_miktar might already be an integer
                if not isinstance(siparis.odenen_miktar, int):
                    siparis.odenen_miktar = int(round(siparis.odenen_miktar))
                siparis.save()
            
            # Convert Odeme model fields
            self.stdout.write('Converting Odeme model fields...')
            for odeme in Odeme.objects.all():
                # Convert to integer by rounding
                if not isinstance(odeme.miktar, int):
                    odeme.miktar = int(round(odeme.miktar))
                odeme.save()
            
            # Convert Malzeme model fields
            self.stdout.write('Converting Malzeme model fields...')
            for malzeme in Malzeme.objects.all():
                # Convert to integer by rounding
                if not isinstance(malzeme.birim_fiyat, int):
                    malzeme.birim_fiyat = int(round(malzeme.birim_fiyat))
                malzeme.save()
            
            # Convert Rapor model fields
            self.stdout.write('Converting Rapor model fields...')
            for rapor in Rapor.objects.all():
                # Convert to integers by rounding
                if not isinstance(rapor.toplam_gelir, int):
                    rapor.toplam_gelir = int(round(rapor.toplam_gelir))
                if not isinstance(rapor.toplam_odenen, int):
                    rapor.toplam_odenen = int(round(rapor.toplam_odenen))
                rapor.save()
        
        self.stdout.write(self.style.SUCCESS('Successfully converted decimal values to integers!'))