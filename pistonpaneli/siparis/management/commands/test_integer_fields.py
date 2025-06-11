from django.core.management.base import BaseCommand
from siparis.models import Siparis, Odeme, Malzeme, Rapor
from django.utils import timezone

class Command(BaseCommand):
    help = 'Test the integer fields in the models'

    def handle(self, *args, **options):
        # Test Siparis model
        self.stdout.write(self.style.SUCCESS('Testing Siparis model...'))
        siparis = Siparis.objects.first()
        if siparis:
            self.stdout.write(f"Siparis birim_fiyat: {siparis.birim_fiyat} (type: {type(siparis.birim_fiyat).__name__})")
            self.stdout.write(f"Siparis toplam_fiyat: {siparis.toplam_fiyat} (type: {type(siparis.toplam_fiyat).__name__})")
            self.stdout.write(f"Siparis odenen_miktar: {siparis.odenen_miktar} (type: {type(siparis.odenen_miktar).__name__})")
        else:
            self.stdout.write(self.style.WARNING('No Siparis objects found'))

        # Test Odeme model
        self.stdout.write(self.style.SUCCESS('Testing Odeme model...'))
        odeme = Odeme.objects.first()
        if odeme:
            self.stdout.write(f"Odeme miktar: {odeme.miktar} (type: {type(odeme.miktar).__name__})")
        else:
            self.stdout.write(self.style.WARNING('No Odeme objects found'))

        # Test Malzeme model
        self.stdout.write(self.style.SUCCESS('Testing Malzeme model...'))
        malzeme = Malzeme.objects.first()
        if malzeme:
            self.stdout.write(f"Malzeme birim_fiyat: {malzeme.birim_fiyat} (type: {type(malzeme.birim_fiyat).__name__})")
        else:
            self.stdout.write(self.style.WARNING('No Malzeme objects found'))

        # Test Rapor model
        self.stdout.write(self.style.SUCCESS('Testing Rapor model...'))
        rapor = Rapor.objects.first()
        if rapor:
            self.stdout.write(f"Rapor toplam_gelir: {rapor.toplam_gelir} (type: {type(rapor.toplam_gelir).__name__})")
            self.stdout.write(f"Rapor toplam_odenen: {rapor.toplam_odenen} (type: {type(rapor.toplam_odenen).__name__})")
            self.stdout.write(f"Rapor tahsilat_orani: {rapor.tahsilat_orani()} (type: {type(rapor.tahsilat_orani()).__name__})")
        else:
            self.stdout.write(self.style.WARNING('No Rapor objects found'))

        # Test creating new objects with integer values
        self.stdout.write(self.style.SUCCESS('Testing creating new objects...'))
        try:
            # Create a test Malzeme
            test_malzeme = Malzeme.objects.create(
                ad="Test Malzeme",
                tur="celik",
                stok_miktari=10,
                birim="adet",
                birim_fiyat=100  # Integer value
            )
            self.stdout.write(f"Created Malzeme with birim_fiyat: {test_malzeme.birim_fiyat} (type: {type(test_malzeme.birim_fiyat).__name__})")
            
            # Clean up
            test_malzeme.delete()
            self.stdout.write(self.style.SUCCESS('Test completed successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating test objects: {e}'))