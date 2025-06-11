from django.core.management.base import BaseCommand
from django.utils import timezone
from siparis.models import Rapor, Siparis
from django.db.models import Count, Sum
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Creates sample reports for the application'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample reports...')
        
        # Check if there are any orders in the system
        if not Siparis.objects.exists():
            self.stdout.write(self.style.ERROR('No orders found. Please create sample data first using the create_sample_data command.'))
            return
        
        # Check if reports already exist
        if Rapor.objects.exists():
            self.stdout.write('Reports already exist, skipping...')
            return
        
        # Create sample reports
        self.create_sample_reports()
        
        self.stdout.write(self.style.SUCCESS('Sample reports created successfully!'))
    
    def create_sample_reports(self):
        # Get the date range of orders
        first_order_date = Siparis.objects.order_by('tarih').first().tarih
        last_order_date = Siparis.objects.order_by('-tarih').first().tarih
        
        # Create daily reports (last 3 days)
        self.create_daily_reports(last_order_date)
        
        # Create weekly reports (last 3 weeks)
        self.create_weekly_reports(last_order_date)
        
        # Create monthly reports (last 3 months)
        self.create_monthly_reports(last_order_date)
        
        # Create a full period report
        self.create_full_period_report(first_order_date, last_order_date)
    
    def create_daily_reports(self, last_date):
        """Create daily reports for the last 3 days with orders"""
        for i in range(3):
            # Get a date with orders
            current_date = last_date - timedelta(days=i)
            
            # Check if there are orders on this date
            orders_on_date = Siparis.objects.filter(tarih=current_date)
            if not orders_on_date.exists():
                continue
            
            # Create report for this day
            report_title = f"Günlük Rapor: {current_date.strftime('%d.%m.%Y')}"
            self.create_report(
                baslik=report_title,
                tip='gunluk',
                baslangic_tarihi=current_date,
                bitis_tarihi=current_date
            )
            
            self.stdout.write(f"Created daily report for {current_date.strftime('%d.%m.%Y')}")
    
    def create_weekly_reports(self, last_date):
        """Create weekly reports for the last 3 weeks"""
        for i in range(3):
            # Calculate week start and end dates
            end_date = last_date - timedelta(days=i*7)
            start_date = end_date - timedelta(days=6)
            
            # Check if there are orders in this week
            orders_in_week = Siparis.objects.filter(tarih__gte=start_date, tarih__lte=end_date)
            if not orders_in_week.exists():
                continue
            
            # Create report for this week
            report_title = f"Haftalık Rapor: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}"
            self.create_report(
                baslik=report_title,
                tip='haftalik',
                baslangic_tarihi=start_date,
                bitis_tarihi=end_date
            )
            
            self.stdout.write(f"Created weekly report for {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
    
    def create_monthly_reports(self, last_date):
        """Create monthly reports for the last 3 months"""
        for i in range(3):
            # Calculate month start and end dates (approximate)
            end_date = last_date.replace(day=1) - timedelta(days=i*30)
            if end_date.month == 12:
                next_month = end_date.replace(year=end_date.year+1, month=1)
            else:
                next_month = end_date.replace(month=end_date.month+1)
            end_date = next_month - timedelta(days=1)
            start_date = end_date.replace(day=1)
            
            # Check if there are orders in this month
            orders_in_month = Siparis.objects.filter(tarih__gte=start_date, tarih__lte=end_date)
            if not orders_in_month.exists():
                continue
            
            # Create report for this month
            month_names = {
                1: 'Ocak', 2: 'Şubat', 3: 'Mart', 4: 'Nisan', 5: 'Mayıs', 6: 'Haziran',
                7: 'Temmuz', 8: 'Ağustos', 9: 'Eylül', 10: 'Ekim', 11: 'Kasım', 12: 'Aralık'
            }
            month_name = month_names[start_date.month]
            report_title = f"Aylık Rapor: {month_name} {start_date.year}"
            self.create_report(
                baslik=report_title,
                tip='aylik',
                baslangic_tarihi=start_date,
                bitis_tarihi=end_date
            )
            
            self.stdout.write(f"Created monthly report for {month_name} {start_date.year}")
    
    def create_full_period_report(self, first_date, last_date):
        """Create a report covering the entire period of orders"""
        report_title = f"Tüm Zamanlar Raporu: {first_date.strftime('%d.%m.%Y')} - {last_date.strftime('%d.%m.%Y')}"
        self.create_report(
            baslik=report_title,
            tip='aylik',  # Using monthly type for full period
            baslangic_tarihi=first_date,
            bitis_tarihi=last_date
        )
        
        self.stdout.write(f"Created full period report from {first_date.strftime('%d.%m.%Y')} to {last_date.strftime('%d.%m.%Y')}")
    
    def create_report(self, baslik, tip, baslangic_tarihi, bitis_tarihi):
        """Helper method to create a report with the given parameters"""
        # Get orders in the date range
        siparisler = Siparis.objects.filter(
            tarih__gte=baslangic_tarihi,
            tarih__lte=bitis_tarihi
        )
        
        # Calculate report statistics
        toplam_siparis = siparisler.count()
        toplam_gelir = siparisler.aggregate(toplam=Sum('toplam_fiyat'))['toplam'] or 0
        
        # Create the report
        Rapor.objects.create(
            baslik=baslik,
            tip=tip,
            baslangic_tarihi=baslangic_tarihi,
            bitis_tarihi=bitis_tarihi,
            toplam_siparis=toplam_siparis,
            toplam_gelir=toplam_gelir
        )