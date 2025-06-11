from django.core.management.base import BaseCommand
from siparis.models import Siparis, Odeme, Malzeme
from django.utils import timezone
from django.conf import settings

class Command(BaseCommand):
    help = 'Test email notification functionality'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing email notification functionality...'))
        
        # Check if email settings are configured
        if not hasattr(settings, 'EMAIL_BACKEND') or not settings.EMAIL_BACKEND:
            self.stdout.write(self.style.ERROR('Email settings are not configured. Please configure EMAIL_BACKEND in settings.py.'))
            return
            
        self.stdout.write(f"Using email backend: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"Default from email: {settings.DEFAULT_FROM_EMAIL}")
        self.stdout.write(f"Admin email: {settings.ADMIN_EMAIL}")
        
        # Test order status notification
        self.test_order_status_notification()
        
        # Test payment notification
        self.test_payment_notification()
        
        # Test critical stock alert
        self.test_critical_stock_alert()
        
        self.stdout.write(self.style.SUCCESS('Email notification tests completed.'))
        
        if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
            self.stdout.write(self.style.WARNING('Note: Using console email backend. Emails are printed to console, not actually sent.'))
            self.stdout.write(self.style.WARNING('Check the console output above to see the email content.'))
    
    def test_order_status_notification(self):
        """Test order status change notification"""
        self.stdout.write(self.style.NOTICE('\nTesting order status notification...'))
        
        # Get the first order or create a test order
        try:
            siparis = Siparis.objects.first()
            if not siparis:
                self.stdout.write(self.style.WARNING('No orders found. Skipping order status notification test.'))
                return
                
            self.stdout.write(f"Using order: {siparis}")
            
            # Change the order status to trigger notification
            old_status = siparis.durum
            
            # Choose a different status
            statuses = ['beklemede', 'uretimde', 'tamamlandi', 'teslim_edildi']
            new_status = next((s for s in statuses if s != old_status), 'beklemede')
            
            self.stdout.write(f"Changing status from '{old_status}' to '{new_status}'")
            
            # Update the status
            siparis.durum = new_status
            siparis.save()
            
            self.stdout.write(self.style.SUCCESS("Order status notification test completed."))
            
            # Restore the original status
            siparis.durum = old_status
            siparis.save(update_fields=['durum'])
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error in order status notification test: {e}"))
    
    def test_payment_notification(self):
        """Test payment notification"""
        self.stdout.write(self.style.NOTICE('\nTesting payment notification...'))
        
        # Get the first order or create a test order
        try:
            siparis = Siparis.objects.first()
            if not siparis:
                self.stdout.write(self.style.WARNING('No orders found. Skipping payment notification test.'))
                return
                
            self.stdout.write(f"Using order: {siparis}")
            
            # Create a test payment
            test_payment = Odeme(
                siparis=siparis,
                miktar=100,  # Small test amount
                aciklama="Test payment for notification"
            )
            
            # Save to trigger notification
            test_payment.save()
            
            self.stdout.write(self.style.SUCCESS("Payment notification test completed."))
            
            # Clean up - delete the test payment
            test_payment.delete()
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error in payment notification test: {e}"))
    
    def test_critical_stock_alert(self):
        """Test critical stock alert"""
        self.stdout.write(self.style.NOTICE('\nTesting critical stock alert...'))
        
        try:
            # Create a test material with stock level above minimum
            test_material = Malzeme(
                ad="Test Material for Notification",
                tur="celik",
                stok_miktari=10,
                birim="adet",
                birim_fiyat=100,
                minimum_stok=5
            )
            
            # Save without triggering notification
            test_material.save()
            
            self.stdout.write(f"Created test material with stock: {test_material.stok_miktari}, minimum: {test_material.minimum_stok}")
            
            # Reduce stock to trigger notification
            self.stdout.write("Reducing stock below minimum level...")
            test_material.stok_miktari = 4  # Below minimum_stok
            test_material.save()
            
            self.stdout.write(self.style.SUCCESS("Critical stock alert test completed."))
            
            # Clean up - delete the test material
            test_material.delete()
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error in critical stock alert test: {e}"))