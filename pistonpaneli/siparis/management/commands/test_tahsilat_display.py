from django.core.management.base import BaseCommand
from siparis.models import Rapor
from siparis.admin import RaporAdmin
from django.utils.html import format_html

class Command(BaseCommand):
    help = 'Test the improved tahsilat_orani_yuzde display'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing improved tahsilat_orani_yuzde display...'))
        
        # Get all reports
        reports = Rapor.objects.all()
        self.stdout.write(f"Found {reports.count()} reports")
        
        # Create an instance of RaporAdmin
        rapor_admin = RaporAdmin(Rapor, None)
        
        for i, rapor in enumerate(reports):
            self.stdout.write(f"\nReport {i+1}: {rapor.baslik}")
            self.stdout.write(f"  toplam_gelir: {rapor.toplam_gelir}")
            self.stdout.write(f"  toplam_odenen: {rapor.toplam_odenen}")
            self.stdout.write(f"  tahsilat_orani: {rapor.tahsilat_orani():.2f}%")
            
            # Get the HTML display
            display_html = rapor_admin.tahsilat_orani_yuzde(rapor)
            
            # Convert to string for display in terminal
            display_str = str(display_html)
            self.stdout.write(f"  Display HTML: {display_str}")
            
            # Check if the display includes the payment information
            if f"{rapor.toplam_odenen:,} / {rapor.toplam_gelir:,} TL" in display_str:
                self.stdout.write(self.style.SUCCESS("  Payment information is included in the display"))
            else:
                self.stdout.write(self.style.ERROR("  Payment information is NOT included in the display"))
        
        # Test with different percentages
        self.stdout.write(self.style.SUCCESS('\nTesting with different percentages...'))
        
        test_cases = [
            {"name": "High (95%)", "gelir": 1000, "odenen": 950},
            {"name": "Medium (75%)", "gelir": 1000, "odenen": 750},
            {"name": "Low (25%)", "gelir": 1000, "odenen": 250},
            {"name": "Zero (0%)", "gelir": 1000, "odenen": 0},
        ]
        
        for case in test_cases:
            test_report = Rapor(
                baslik=f"Test {case['name']}",
                tip="ozel",
                baslangic_tarihi="2023-01-01",
                bitis_tarihi="2023-01-31",
                toplam_siparis=10,
                toplam_gelir=case["gelir"],
                toplam_odenen=case["odenen"]
            )
            
            display_html = rapor_admin.tahsilat_orani_yuzde(test_report)
            display_str = str(display_html)
            
            expected_ratio = (case["odenen"] / case["gelir"]) * 100 if case["gelir"] > 0 else 0
            
            self.stdout.write(f"\nTest case: {case['name']}")
            self.stdout.write(f"  Expected ratio: {expected_ratio:.2f}%")
            self.stdout.write(f"  Display HTML: {display_str}")
            
            # Check if the display includes the expected percentage
            if f"%{expected_ratio:.2f}" in display_str or f"%{expected_ratio:.1f}" in display_str:
                self.stdout.write(self.style.SUCCESS("  Percentage is correctly displayed"))
            else:
                self.stdout.write(self.style.ERROR("  Percentage is NOT correctly displayed"))
                
            # Check if the display includes the payment information
            if f"{case['odenen']:,} / {case['gelir']:,} TL" in display_str:
                self.stdout.write(self.style.SUCCESS("  Payment information is correctly displayed"))
            else:
                self.stdout.write(self.style.ERROR("  Payment information is NOT correctly displayed"))
        
        self.stdout.write(self.style.SUCCESS('\nTest completed'))