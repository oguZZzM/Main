from django.core.management.base import BaseCommand
from django.utils import timezone
from siparis.models import Musteri, Malzeme, Siparis, MalzemeKullanimi
from decimal import Decimal
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Creates sample data for the application'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create sample customers
        self.create_sample_customers()
        
        # Create sample materials
        self.create_sample_materials()
        
        # Create sample orders
        self.create_sample_orders()
        
        # Create sample material usage
        self.create_sample_material_usage()
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
    
    def create_sample_customers(self):
        # Check if customers already exist
        if Musteri.objects.exists():
            self.stdout.write('Customers already exist, skipping...')
            return
        
        customers = [
            {'isim': 'Ahmet Yılmaz', 'telefon': '0555 123 4567', 'adres': 'İstanbul, Kadıköy', 'firmasi': 'Yılmaz Makina'},
            {'isim': 'Mehmet Demir', 'telefon': '0532 987 6543', 'adres': 'Ankara, Çankaya', 'firmasi': 'Demir Sanayi'},
            {'isim': 'Ayşe Kaya', 'telefon': '0533 456 7890', 'adres': 'İzmir, Konak', 'firmasi': 'Kaya Mühendislik'},
            {'isim': 'Fatma Şahin', 'telefon': '0542 345 6789', 'adres': 'Bursa, Nilüfer', 'firmasi': 'Şahin Otomotiv'},
            {'isim': 'Ali Öztürk', 'telefon': '0535 678 9012', 'adres': 'Antalya, Muratpaşa', 'firmasi': 'Öztürk Hidrolik'},
            {'isim': 'Zeynep Çelik', 'telefon': '0536 789 0123', 'adres': 'Adana, Seyhan', 'firmasi': 'Çelik Metal'},
            {'isim': 'Mustafa Aydın', 'telefon': '0537 890 1234', 'adres': 'Konya, Selçuklu', 'firmasi': 'Aydın Makina'},
            {'isim': 'Hüseyin Yıldız', 'telefon': '0538 901 2345', 'adres': 'Kayseri, Melikgazi', 'firmasi': 'Yıldız Piston'},
            {'isim': 'Emine Arslan', 'telefon': '0539 012 3456', 'adres': 'Eskişehir, Tepebaşı', 'firmasi': 'Arslan Sanayi'},
            {'isim': 'Osman Kılıç', 'telefon': '0540 123 4567', 'adres': 'Gaziantep, Şahinbey', 'firmasi': 'Kılıç Hidrolik'},
        ]
        
        for customer_data in customers:
            Musteri.objects.create(**customer_data)
            
        self.stdout.write(f'Created {len(customers)} sample customers')
    
    def create_sample_materials(self):
        # Check if materials already exist
        if Malzeme.objects.exists():
            self.stdout.write('Materials already exist, skipping...')
            return
        
        materials = [
            {'ad': 'Çelik Mil 10mm', 'tur': 'celik', 'stok_miktari': 50, 'birim': 'metre', 'birim_fiyat': Decimal('25.50'), 'aciklama': '10mm çapında çelik mil'},
            {'ad': 'Çelik Mil 20mm', 'tur': 'celik', 'stok_miktari': 40, 'birim': 'metre', 'birim_fiyat': Decimal('45.75'), 'aciklama': '20mm çapında çelik mil'},
            {'ad': 'Çelik Mil 30mm', 'tur': 'celik', 'stok_miktari': 30, 'birim': 'metre', 'birim_fiyat': Decimal('65.00'), 'aciklama': '30mm çapında çelik mil'},
            {'ad': 'Alüminyum Profil 20x20', 'tur': 'aluminyum', 'stok_miktari': 100, 'birim': 'metre', 'birim_fiyat': Decimal('18.25'), 'aciklama': '20x20mm alüminyum profil'},
            {'ad': 'Alüminyum Profil 30x30', 'tur': 'aluminyum', 'stok_miktari': 80, 'birim': 'metre', 'birim_fiyat': Decimal('27.50'), 'aciklama': '30x30mm alüminyum profil'},
            {'ad': 'Paslanmaz Çelik Plaka 2mm', 'tur': 'paslanmaz', 'stok_miktari': 20, 'birim': 'adet', 'birim_fiyat': Decimal('120.00'), 'aciklama': '2mm kalınlığında paslanmaz çelik plaka'},
            {'ad': 'Bronz Burç 15mm', 'tur': 'bronz', 'stok_miktari': 60, 'birim': 'adet', 'birim_fiyat': Decimal('8.50'), 'aciklama': '15mm iç çaplı bronz burç'},
            {'ad': 'Bronz Burç 25mm', 'tur': 'bronz', 'stok_miktari': 45, 'birim': 'adet', 'birim_fiyat': Decimal('12.75'), 'aciklama': '25mm iç çaplı bronz burç'},
            {'ad': 'Bakır Boru 15mm', 'tur': 'bakir', 'stok_miktari': 35, 'birim': 'metre', 'birim_fiyat': Decimal('32.00'), 'aciklama': '15mm çapında bakır boru'},
            {'ad': 'Plastik Kapak 50mm', 'tur': 'plastik', 'stok_miktari': 200, 'birim': 'adet', 'birim_fiyat': Decimal('3.25'), 'aciklama': '50mm çapında plastik kapak'},
            {'ad': 'Kauçuk Conta 20mm', 'tur': 'kaucuk', 'stok_miktari': 150, 'birim': 'adet', 'birim_fiyat': Decimal('1.50'), 'aciklama': '20mm çapında kauçuk conta'},
            {'ad': 'Krom Kaplama Solüsyonu', 'tur': 'krom', 'stok_miktari': 10, 'birim': 'litre', 'birim_fiyat': Decimal('85.00'), 'aciklama': 'Krom kaplama için solüsyon'},
            {'ad': 'Yağlama Gresi', 'tur': 'diger', 'stok_miktari': 25, 'birim': 'kg', 'birim_fiyat': Decimal('45.00'), 'aciklama': 'Endüstriyel yağlama gresi'},
            {'ad': 'Temizleme Solüsyonu', 'tur': 'diger', 'stok_miktari': 15, 'birim': 'litre', 'birim_fiyat': Decimal('35.00'), 'aciklama': 'Metal yüzey temizleme solüsyonu'},
            {'ad': 'Çelik Piston Kolu 40mm', 'tur': 'celik', 'stok_miktari': 25, 'birim': 'adet', 'birim_fiyat': Decimal('95.00'), 'aciklama': '40mm çapında çelik piston kolu'},
        ]
        
        for material_data in materials:
            Malzeme.objects.create(**material_data)
            
        self.stdout.write(f'Created {len(materials)} sample materials')
    
    def create_sample_orders(self):
        # Check if orders already exist
        if Siparis.objects.exists():
            self.stdout.write('Orders already exist, skipping...')
            return
        
        # Get all customers
        customers = list(Musteri.objects.all())
        if not customers:
            self.stdout.write(self.style.ERROR('No customers found. Please create customers first.'))
            return
        
        # Order data
        order_types = [
            'Piston Kolu',
            'Hidrolik Silindir',
            'Şaft',
            'Mil',
            'Burç',
            'Kapak',
            'Conta',
            'Valf Bloğu',
            'Hidrolik Pompa',
            'Filtre Elemanı'
        ]
        
        statuses = ['beklemede', 'uretimde', 'tamamlandi', 'teslim_edildi', 'iptal_edildi']
        iscilik_turleri = ['taslama', 'krom_kaplama', 'honlama', 'polisaj', 'diger']
        
        # Create 20 sample orders
        for i in range(20):
            customer = random.choice(customers)
            order_type = random.choice(order_types)
            status = random.choice(statuses)
            iscilik_turu = random.choice(iscilik_turleri)
            
            # Random dates within the last 60 days
            days_ago = random.randint(0, 60)
            order_date = timezone.now().date() - timedelta(days=days_ago)
            
            # Random quantities and prices
            quantity = random.randint(1, 10)
            unit_price = Decimal(str(random.uniform(50, 500)))
            unit_price = unit_price.quantize(Decimal('0.01'))  # Round to 2 decimal places
            
            # Random priority
            priority = random.randint(0, 5)
            
            # Create the order
            order = Siparis.objects.create(
                musteri=customer,
                urun_tipi=order_type,
                adet=quantity,
                iscilik_turu=iscilik_turu,
                durum=status,
                birim_fiyat=unit_price,
                aciklama=f'Örnek sipariş #{i+1} açıklaması. Ölçüler ve detaylar burada belirtilir.',
                oncelik=priority,
                tarih=order_date
            )
            
            # If the order is completed or delivered, set a delivery date
            if status in ['tamamlandi', 'teslim_edildi']:
                delivery_days = random.randint(1, 30)
                delivery_date = order_date + timedelta(days=delivery_days)
                order.teslim_tarihi = delivery_date
                order.save()
            
            # Add some payments for some orders
            if random.random() > 0.3:  # 70% chance of having a payment
                payment_percentage = random.choice([0.3, 0.5, 0.7, 1.0])  # Different payment percentages
                payment_amount = order.toplam_fiyat * Decimal(str(payment_percentage))
                payment_amount = payment_amount.quantize(Decimal('0.01'))  # Round to 2 decimal places
                order.odeme_yap(payment_amount, f'Örnek ödeme #{i+1}')
        
        self.stdout.write(f'Created 20 sample orders')
    
    def create_sample_material_usage(self):
        # Check if material usage records already exist
        if MalzemeKullanimi.objects.exists():
            self.stdout.write('Material usage records already exist, skipping...')
            return
        
        # Get all orders and materials
        orders = list(Siparis.objects.all())
        materials = list(Malzeme.objects.all())
        
        if not orders or not materials:
            self.stdout.write(self.style.ERROR('No orders or materials found. Please create them first.'))
            return
        
        # Create material usage records
        usage_records = []
        
        # For each order, use 1-3 different materials
        for order in orders:
            # Skip some orders randomly
            if random.random() > 0.8:  # 80% chance of having material usage
                continue
                
            # Select 1-3 random materials for this order
            num_materials = random.randint(1, 3)
            order_materials = random.sample(materials, min(num_materials, len(materials)))
            
            for material in order_materials:
                # Random quantity
                quantity = random.randint(1, 5)
                
                # Ensure we don't exceed the stock
                if quantity > material.stok_miktari:
                    quantity = material.stok_miktari
                
                if quantity > 0:
                    try:
                        # Create the usage record
                        usage = MalzemeKullanimi.objects.create(
                            siparis=order,
                            malzeme=material,
                            miktar=quantity
                        )
                        usage_records.append(usage)
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error creating material usage: {str(e)}'))
        
        self.stdout.write(f'Created {len(usage_records)} sample material usage records')