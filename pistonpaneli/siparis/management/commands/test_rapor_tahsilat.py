from django.core.management.base import BaseCommand
from siparis.models import Rapor
from django.utils import timezone

class Command(BaseCommand):
    help = 'Test the tahsilat_orani calculation in Rapor model'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing Rapor tahsilat_orani calculation...'))
        
        # Get all reports
        reports = Rapor.objects.all()
        self.stdout.write(f"Found {reports.count()} reports")
        
        for i, rapor in enumerate(reports):
            self.stdout.write(f"\nReport {i+1}: {rapor.baslik}")
            self.stdout.write(f"  toplam_gelir: {rapor.toplam_gelir} (type: {type(rapor.toplam_gelir).__name__})")
            self.stdout.write(f"  toplam_odenen: {rapor.toplam_odenen} (type: {type(rapor.toplam_odenen).__name__})")
            
            # Calculate tahsilat_orani
            try:
                oran = rapor.tahsilat_orani()
                self.stdout.write(f"  tahsilat_orani: {oran:.2f}% (type: {type(oran).__name__})")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Error calculating tahsilat_orani: {e}"))
            
            # Manual calculation for verification
            try:
                if rapor.toplam_gelir > 0:
                    manual_oran = (float(rapor.toplam_odenen) / rapor.toplam_gelir) * 100
                    self.stdout.write(f"  Manual calculation: {manual_oran:.2f}%")
                else:
                    self.stdout.write(f"  Manual calculation: 0.00% (toplam_gelir is {rapor.toplam_gelir})")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Error in manual calculation: {e}"))
        
        # Create a test report with known values
        self.stdout.write(self.style.SUCCESS('\nCreating a test report with known values...'))
        try:
            test_report = Rapor(
                baslik="Test Report",
                tip="ozel",
                baslangic_tarihi=timezone.now().date(),
                bitis_tarihi=timezone.now().date(),
                toplam_siparis=10,
                toplam_gelir=1000,
                toplam_odenen=750
            )
            
            # Calculate without saving
            expected_ratio = 75.0  # 750/1000 * 100
            actual_ratio = (float(test_report.toplam_odenen) / test_report.toplam_gelir) * 100
            self.stdout.write(f"  Expected ratio: {expected_ratio:.2f}%")
            self.stdout.write(f"  Actual ratio: {actual_ratio:.2f}%")
            
            # Test the model method
            model_ratio = test_report.tahsilat_orani()
            self.stdout.write(f"  Model method ratio: {model_ratio:.2f}%")
            
            if abs(model_ratio - expected_ratio) < 0.01:
                self.stdout.write(self.style.SUCCESS("  Test passed: Model method calculation is correct"))
            else:
                self.stdout.write(self.style.ERROR(f"  Test failed: Expected {expected_ratio:.2f}%, got {model_ratio:.2f}%"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  Error creating test report: {e}"))
        
        self.stdout.write(self.style.SUCCESS('\nTest completed'))