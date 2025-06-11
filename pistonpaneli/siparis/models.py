from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

class Musteri(models.Model):
    """
    Müşteri bilgilerini saklayan model.

    Bu model, müşteri adı, telefon, adres ve firma bilgilerini içerir.
    Müşteriler siparişlerle ilişkilendirilir.
    """
    isim = models.CharField(max_length=120, help_text="Müşteri adı ve soyadı")
    telefon_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Telefon numarası '+999999999' formatında olmalıdır."
    )
    telefon = models.CharField(
        validators=[telefon_regex], 
        max_length=20, 
        blank=True, 
        help_text="İletişim telefon numarası"
    )
    adres = models.TextField(blank=True, help_text="Müşteri adresi")
    firmasi = models.CharField(max_length=150, blank=True, help_text="Müşterinin çalıştığı firma")
    kayit_tarihi = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Müşteri'
        verbose_name_plural = 'Müşteriler'
        ordering = ['-kayit_tarihi', 'isim']  # Sıralama: önce yeni kayıtlar, sonra isme göre

    def __str__(self):
        if self.firmasi:
            return f"{self.isim} ({self.firmasi})"
        return self.isim

    def toplam_siparis_sayisi(self):
        """Müşterinin toplam sipariş sayısını döndürür"""
        return self.siparisler.count()

    def toplam_borc(self):
        """Müşterinin toplam borç miktarını hesaplar"""
        from django.db.models import Sum
        return self.siparisler.aggregate(toplam=Sum('toplam_fiyat'))['toplam'] or 0

    def odenen_miktar(self):
        """Müşterinin toplam ödediği miktarı hesaplar"""
        from django.db.models import Sum
        return self.siparisler.aggregate(toplam=Sum('odenen_miktar'))['toplam'] or 0

    def kalan_borc(self):
        """Müşterinin kalan borç miktarını hesaplar"""
        return self.toplam_borc() - self.odenen_miktar()



class Siparis(models.Model):
    """
    Sipariş bilgilerini saklayan model.

    Bu model, müşteri siparişlerini, ürün bilgilerini, işçilik türünü, 
    durum bilgilerini ve ödeme detaylarını içerir.
    """
    DURUM_SECENEKLERI = [
        ('beklemede', 'Beklemede'),
        ('uretimde', 'Üretimde'),
        ('tamamlandi', 'Tamamlandı'),
        ('teslim_edildi', 'Teslim Edildi'),
        ('iptal_edildi', 'İptal Edildi'),
    ]

    ISCIK_TURU_SECENEKLERI = [
        ('taslama', 'Silindirik Piston Taşlama'),
        ('krom_kaplama', 'Sert Krom Kaplama'),
        ('honlama', 'Honlama'),
        ('polisaj', 'Polisaj'),
        ('diger', 'Diğer İşlemler'),
    ]

    ODEME_DURUMU_SECENEKLERI = [
        ('odenmedi', 'Ödenmedi'),
        ('kismi_odendi', 'Kısmen Ödendi'),
        ('odendi', 'Ödendi'),
    ]

    ONCELIK_SECENEKLERI = [
        (0, 'Normal'),
        (1, 'Yüksek'),
        (2, 'Acil'),
    ]

    class Meta:
        verbose_name = 'Sipariş'
        verbose_name_plural = 'Siparişler'
        ordering = ['-oncelik', '-tarih']  # Önce öncelikli, sonra yeni siparişler

    musteri = models.ForeignKey(
        Musteri, 
        on_delete=models.CASCADE, 
        related_name='siparisler',
        help_text="Siparişi veren müşteri"
    )
    urun_tipi = models.CharField(
        max_length=200, 
        help_text="Örn: Piston kolu, şaft vb."
    )
    adet = models.PositiveIntegerField(
        default=1, 
        help_text="Sipariş adedi"
    )
    iscilik_turu = models.CharField(
        max_length=50, 
        choices=ISCIK_TURU_SECENEKLERI,
        help_text="Yapılacak işçilik türü"
    )
    tarih = models.DateField(
        auto_now_add=True,
        help_text="Siparişin oluşturulma tarihi"
    )
    teslim_tarihi = models.DateField(
        null=True, 
        blank=True, 
        help_text="Siparişin teslim edildiği tarih"
    )
    durum = models.CharField(
        max_length=20, 
        choices=DURUM_SECENEKLERI, 
        default='beklemede',
        help_text="Siparişin mevcut durumu"
    )
    aciklama = models.TextField(
        blank=True, 
        help_text="Ekstra bilgiler ve ölçüler (ölçü, çap, uzunluk vb.)"
    )
    birim_fiyat = models.IntegerField(
        default=0, 
        help_text="Birim fiyat (TL)"
    )
    toplam_fiyat = models.IntegerField(
        default=0, 
        help_text="Toplam fiyat (TL)",
        editable=False  # Otomatik hesaplanacak
    )
    odeme_durumu = models.CharField(
        max_length=20, 
        choices=ODEME_DURUMU_SECENEKLERI, 
        default='odenmedi',
        help_text="Ödeme durumu",
        editable=False  # Otomatik hesaplanacak
    )
    odenen_miktar = models.IntegerField(
        default=0, 
        help_text="Ödenen miktar (TL)"
    )
    oncelik = models.PositiveSmallIntegerField(
        default=0, 
        choices=ONCELIK_SECENEKLERI,
        help_text="Siparişin öncelik seviyesi"
    )

    def __str__(self):
        return f"{self.musteri.isim} - {self.urun_tipi} ({self.adet} adet) [{self.get_iscilik_turu_display()}]"

    def save(self, *args, **kwargs):
        # Durum değişikliğini kontrol etmek için eski durumu kaydet
        try:
            old_instance = Siparis.objects.get(pk=self.pk)
            old_status = old_instance.durum
        except (Siparis.DoesNotExist, ValueError):
            old_status = None

        # Toplam fiyatı hesapla
        self.toplam_fiyat = self.birim_fiyat * self.adet

        # Ödeme durumunu güncelle
        if self.odenen_miktar <= 0:
            self.odeme_durumu = 'odenmedi'
        elif self.odenen_miktar < self.toplam_fiyat:
            self.odeme_durumu = 'kismi_odendi'
        else:
            self.odeme_durumu = 'odendi'

        # Eğer durum "teslim_edildi" ise ve teslim_tarihi boşsa, bugünün tarihini ata
        if self.durum == 'teslim_edildi' and not self.teslim_tarihi:
            self.teslim_tarihi = timezone.now().date()

        # Kaydı gerçekleştir
        super().save(*args, **kwargs)

        # Durum değişikliği varsa bildirim gönder
        if old_status and old_status != self.durum:
            try:
                from .utils import send_order_status_notification
                send_order_status_notification(self)
            except ImportError:
                # Eğer utils modülü henüz yüklenmemişse sessizce devam et
                pass

    def kalan_odeme(self):
        """Kalan ödeme miktarını hesaplar"""
        return max(0, self.toplam_fiyat - self.odenen_miktar)

    def odeme_yap(self, miktar, aciklama=""):
        """
        Siparişe ödeme ekler ve ödeme kaydı oluşturur

        Parametreler:
            miktar (int): Ödeme miktarı
            aciklama (str, isteğe bağlı): Ödeme hakkında açıklama

        Dönüş Değeri:
            Odeme: Oluşturulan ödeme kaydı

        Hatalar:
            ValueError: Eğer miktar negatif veya kalan ödemeden fazlaysa
        """
        if miktar <= 0:
            raise ValueError("Ödeme miktarı sıfırdan büyük olmalıdır.")

        if miktar > self.kalan_odeme():
            raise ValueError(f"Ödeme miktarı kalan ödemeden ({self.kalan_odeme()} TL) fazla olamaz.")

        self.odenen_miktar += miktar
        self.save()

        # Ödeme kaydı oluştur
        return Odeme.objects.create(
            siparis=self,
            miktar=miktar,
            aciklama=aciklama
        )

    def gecikme_suresi(self):
        """
        Siparişin teslim edilmesi gereken tarihten bu yana geçen gün sayısını hesaplar.
        Eğer sipariş tamamlanmışsa veya teslim edilmişse 0 döner.
        """
        if self.durum in ['tamamlandi', 'teslim_edildi', 'iptal_edildi']:
            return 0

        # Eğer teslim tarihi belirtilmişse ve bu tarih geçmişse
        if self.teslim_tarihi and self.teslim_tarihi < timezone.now().date():
            return (timezone.now().date() - self.teslim_tarihi).days
        return 0

    def siparis_yasi(self):
        """Siparişin oluşturulmasından bu yana geçen gün sayısını hesaplar"""
        if self.tarih is None:
            return 0
        return (timezone.now().date() - self.tarih).days


class Odeme(models.Model):
    """
    Sipariş ödemelerini takip etmek için model.

    Bu model, siparişlere yapılan ödemelerin tarih, miktar ve açıklama bilgilerini içerir.
    Her ödeme bir siparişle ilişkilendirilir.
    """
    siparis = models.ForeignKey(
        Siparis, 
        on_delete=models.CASCADE, 
        related_name='odemeler',
        help_text="Ödemenin yapıldığı sipariş"
    )
    tarih = models.DateTimeField(
        auto_now_add=True,
        help_text="Ödemenin yapıldığı tarih ve saat"
    )
    miktar = models.IntegerField(
        help_text="Ödeme miktarı (TL)"
    )
    aciklama = models.CharField(
        max_length=255, 
        blank=True,
        help_text="Ödeme hakkında ek bilgiler (ödeme yöntemi, makbuz no vb.)"
    )

    class Meta:
        verbose_name = 'Ödeme'
        verbose_name_plural = 'Ödemeler'
        ordering = ['-tarih']  # En son yapılan ödemeler önce gösterilir

    def __str__(self):
        return f"{self.siparis} - {self.miktar} TL ({self.tarih.strftime('%d.%m.%Y')})"

    def save(self, *args, **kwargs):
        # Ödeme miktarının pozitif olduğunu kontrol et
        if self.miktar <= 0:
            raise ValueError("Ödeme miktarı sıfırdan büyük olmalıdır.")

        # Yeni kayıt mı kontrol et
        is_new = self.pk is None

        super().save(*args, **kwargs)

        # Yeni ödeme kaydı oluşturulduğunda bildirim gönder
        if is_new:
            try:
                from .utils import send_payment_notification
                send_payment_notification(self)
            except ImportError:
                # Eğer utils modülü henüz yüklenmemişse sessizce devam et
                pass


class Malzeme(models.Model):
    """
    Stokta tutulan malzemeleri takip etmek için model.

    Bu model, envanterdeki malzemelerin türü, miktarı, fiyatı ve diğer 
    özelliklerini takip eder. Malzemeler siparişlerde kullanılabilir.
    Stok seviyesi minimum seviyenin altına düştüğünde otomatik bildirim gönderilir.
    """
    MALZEME_TURU_SECENEKLERI = [
        ('celik', 'Çelik'),
        ('aluminyum', 'Alüminyum'),
        ('paslanmaz', 'Paslanmaz Çelik'),
        ('bronz', 'Bronz'),
        ('bakir', 'Bakır'),
        ('plastik', 'Plastik'),
        ('kaucuk', 'Kauçuk'),
        ('krom', 'Krom'),
        ('diger', 'Diğer'),
    ]

    BIRIM_SECENEKLERI = [
        ('adet', 'Adet'),
        ('kg', 'Kilogram'),
        ('gr', 'Gram'),
        ('lt', 'Litre'),
        ('mt', 'Metre'),
        ('cm', 'Santimetre'),
        ('m2', 'Metrekare'),
        ('m3', 'Metreküp'),
        ('paket', 'Paket'),
        ('kutu', 'Kutu'),
    ]

    ad = models.CharField(
        max_length=100,
        help_text="Malzemenin adı"
    )
    tur = models.CharField(
        max_length=20, 
        choices=MALZEME_TURU_SECENEKLERI, 
        default='diger', 
        verbose_name='Malzeme Türü',
        help_text="Malzemenin türü/kategorisi"
    )
    stok_miktari = models.PositiveIntegerField(
        default=0,
        help_text="Mevcut stok miktarı"
    )
    birim = models.CharField(
        max_length=20, 
        choices=BIRIM_SECENEKLERI,
        default="adet",
        help_text="Stok miktarı birimi (adet, kg, lt vb.)"
    )
    birim_fiyat = models.IntegerField(
        default=0,
        help_text="Birim başına fiyat (TL)"
    )
    aciklama = models.TextField(
        blank=True, 
        help_text="Malzeme hakkında detaylı bilgi"
    )
    son_guncelleme = models.DateTimeField(
        auto_now=True,
        help_text="Son güncelleme tarihi"
    )
    minimum_stok = models.PositiveIntegerField(
        default=5,
        help_text="Uyarı verilecek minimum stok seviyesi"
    )

    class Meta:
        verbose_name = 'Malzeme'
        verbose_name_plural = 'Malzemeler'
        ordering = ['ad']  # Malzemeleri isme göre sırala

    def __str__(self):
        return f"{self.ad} ({self.get_tur_display()}) - {self.stok_miktari} {self.birim}"

    def stok_ekle(self, miktar):
        """
        Stok miktarını artırır

        Parametreler:
            miktar (int): Eklenecek miktar

        Hatalar:
            ValueError: Eğer miktar negatifse
        """
        if miktar <= 0:
            raise ValueError("Eklenecek miktar sıfırdan büyük olmalıdır.")

        self.stok_miktari += miktar
        self.save()

    def stok_cikar(self, miktar):
        """
        Stok miktarını azaltır

        Parametreler:
            miktar (int): Çıkarılacak miktar

        Hatalar:
            ValueError: Eğer miktar negatifse veya mevcut stoktan fazlaysa
        """
        if miktar <= 0:
            raise ValueError("Çıkarılacak miktar sıfırdan büyük olmalıdır.")

        if miktar > self.stok_miktari:
            raise ValueError(f"Yetersiz stok: {self.stok_miktari} {self.birim} mevcut, {miktar} {self.birim} talep edildi")

        # Stok seviyesini kontrol et
        old_stock = self.stok_miktari

        # Stok miktarını azalt
        self.stok_miktari -= miktar
        self.save()

        # Stok seviyesi kritik seviyenin altına düştüyse ve daha önce kritik değilse bildirim gönder
        # Bu kontrol save() metodunda da yapılıyor, ancak burada daha spesifik bir kontrol yapıyoruz
        if (old_stock > self.minimum_stok and 
            self.stok_miktari <= self.minimum_stok):
            try:
                from .utils import send_critical_stock_alert
                send_critical_stock_alert(self)
            except ImportError:
                # Eğer utils modülü henüz yüklenmemişse sessizce devam et
                pass

    def stok_durumu_kritik_mi(self):
        """
        Stok miktarının kritik seviyenin altında olup olmadığını kontrol eder

        Dönüş Değeri:
            bool: Stok kritik seviyenin altındaysa True, değilse False
        """
        return self.stok_miktari <= self.minimum_stok

    def save(self, *args, **kwargs):
        # Eski stok miktarını kontrol etmek için eski nesneyi kaydet
        try:
            old_instance = Malzeme.objects.get(pk=self.pk)
            old_stock = old_instance.stok_miktari
        except (Malzeme.DoesNotExist, ValueError):
            old_stock = None

        # Kaydı gerçekleştir
        super().save(*args, **kwargs)

        # Stok seviyesi kritik seviyenin altına düştüyse bildirim gönder
        # Sadece stok miktarı değiştiğinde ve kritik seviyenin altına düştüğünde bildirim gönder
        if (old_stock is not None and 
            old_stock > self.minimum_stok and 
            self.stok_miktari <= self.minimum_stok):
            try:
                from .utils import send_critical_stock_alert
                send_critical_stock_alert(self)
            except ImportError:
                # Eğer utils modülü henüz yüklenmemişse sessizce devam et
                pass

    def toplam_deger(self):
        """
        Malzemenin toplam stok değerini hesaplar

        Dönüş Değeri:
            Decimal: Toplam stok değeri (stok_miktari * birim_fiyat)
        """
        return self.stok_miktari * self.birim_fiyat


class MalzemeKullanimi(models.Model):
    """
    Siparişlerde kullanılan malzemeleri takip etmek için model.

    Bu model, her siparişte hangi malzemelerin ne miktarda kullanıldığını takip eder.
    Malzeme kullanımı kaydedildiğinde otomatik olarak stok miktarı güncellenir.
    """
    siparis = models.ForeignKey(
        Siparis, 
        on_delete=models.CASCADE, 
        related_name='kullanilan_malzemeler',
        help_text="Malzemenin kullanıldığı sipariş"
    )
    malzeme = models.ForeignKey(
        Malzeme, 
        on_delete=models.PROTECT,  # Malzeme silinirse kullanım kayıtları korunur
        related_name='kullanim_kayitlari',
        help_text="Kullanılan malzeme"
    )
    miktar = models.PositiveIntegerField(
        help_text="Kullanılan miktar"
    )
    tarih = models.DateTimeField(
        auto_now_add=True,
        help_text="Kullanım kaydının oluşturulma tarihi"
    )
    aciklama = models.CharField(
        max_length=255, 
        blank=True,
        help_text="Kullanım hakkında ek bilgiler"
    )

    class Meta:
        verbose_name = 'Malzeme Kullanımı'
        verbose_name_plural = 'Malzeme Kullanımları'
        ordering = ['-tarih']  # En son kullanımlar önce gösterilir
        unique_together = ['siparis', 'malzeme']  # Aynı siparişte aynı malzeme için tek kayıt olabilir

    def __str__(self):
        return f"{self.siparis} - {self.malzeme} ({self.miktar} {self.malzeme.birim})"

    def clean(self):
        """Model validasyonu - miktar ve stok kontrolü"""
        from django.core.exceptions import ValidationError

        if self.miktar <= 0:
            raise ValidationError({'miktar': 'Miktar sıfırdan büyük olmalıdır.'})

        # Yeni kayıt oluşturuluyorsa stok kontrolü yap
        if not self.pk and self.miktar > self.malzeme.stok_miktari:
            raise ValidationError({
                'miktar': f'Yetersiz stok: {self.malzeme.stok_miktari} {self.malzeme.birim} mevcut, '
                          f'{self.miktar} {self.malzeme.birim} talep edildi'
            })

    def save(self, *args, **kwargs):
        # Validasyon yap
        self.full_clean()

        # Yeni kayıt oluşturuluyorsa stoktan düş
        if not self.pk:
            self.malzeme.stok_cikar(self.miktar)
        else:
            # Mevcut kaydı güncelliyorsa, miktar farkını hesapla
            eski_kayit = MalzemeKullanimi.objects.get(pk=self.pk)
            if self.miktar != eski_kayit.miktar:
                fark = self.miktar - eski_kayit.miktar
                if fark > 0:
                    # Miktar artmış, stoktan düş
                    self.malzeme.stok_cikar(fark)
                else:
                    # Miktar azalmış, stoğa ekle
                    self.malzeme.stok_ekle(abs(fark))

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Kayıt siliniyorsa stoğa geri ekle
        self.malzeme.stok_ekle(self.miktar)
        super().delete(*args, **kwargs)

    def toplam_deger(self):
        """
        Kullanılan malzemenin toplam değerini hesaplar

        Dönüş Değeri:
            int: Toplam değer (miktar * birim_fiyat)
        """
        return self.miktar * self.malzeme.birim_fiyat


class Rapor(models.Model):
    """
    Periyodik raporları saklamak için model.

    Bu model, belirli zaman aralıklarında oluşturulan raporları saklar.
    Raporlar günlük, haftalık veya aylık olabilir ve sipariş ve gelir istatistiklerini içerir.
    """
    RAPOR_TIPLERI = [
        ('gunluk', 'Günlük Rapor'),
        ('haftalik', 'Haftalık Rapor'),
        ('aylik', 'Aylık Rapor'),
        ('ozel', 'Özel Rapor'),
        ('yillik', 'Yıllık Rapor'),
    ]

    baslik = models.CharField(
        max_length=100,
        help_text="Raporun başlığı"
    )
    tip = models.CharField(
        max_length=20, 
        choices=RAPOR_TIPLERI,
        help_text="Raporun tipi"
    )
    baslangic_tarihi = models.DateField(
        help_text="Rapor dönemi başlangıç tarihi"
    )
    bitis_tarihi = models.DateField(
        help_text="Rapor dönemi bitiş tarihi"
    )
    olusturulma_tarihi = models.DateTimeField(
        auto_now_add=True,
        help_text="Raporun oluşturulma tarihi ve saati"
    )
    toplam_siparis = models.IntegerField(
        default=0,
        help_text="Rapor dönemindeki toplam sipariş sayısı"
    )
    toplam_gelir = models.IntegerField(
        default=0,
        help_text="Rapor dönemindeki toplam gelir (TL)"
    )
    toplam_odenen = models.IntegerField(
        default=0,
        help_text="Rapor dönemindeki toplam tahsil edilen miktar (TL)"
    )
    aciklama = models.TextField(
        blank=True,
        help_text="Rapor hakkında ek bilgiler"
    )

    class Meta:
        verbose_name = 'Rapor'
        verbose_name_plural = 'Raporlar'
        ordering = ['-olusturulma_tarihi']  # En son oluşturulan raporlar önce gösterilir

    def __str__(self):
        return f"{self.get_tip_display()}: {self.baslik} ({self.baslangic_tarihi} - {self.bitis_tarihi})"

    def clean(self):
        """Model validasyonu - tarih kontrolü"""
        from django.core.exceptions import ValidationError

        if self.bitis_tarihi < self.baslangic_tarihi:
            raise ValidationError({
                'bitis_tarihi': 'Bitiş tarihi başlangıç tarihinden önce olamaz.'
            })

    def save(self, *args, **kwargs):
        # Validasyon yap
        self.full_clean()

        # Eğer istatistikler hesaplanmamışsa, otomatik hesapla
        if self.toplam_siparis == 0 or self.toplam_gelir == 0:
            self.hesapla_istatistikler()

        super().save(*args, **kwargs)

    def hesapla_istatistikler(self):
        """Rapor dönemindeki sipariş ve gelir istatistiklerini hesaplar"""
        from django.db.models import Count, Sum

        # Rapor dönemindeki siparişleri bul
        siparisler = Siparis.objects.filter(
            tarih__gte=self.baslangic_tarihi,
            tarih__lte=self.bitis_tarihi
        )

        # İstatistikleri hesapla
        self.toplam_siparis = siparisler.count()
        toplam_gelir = siparisler.aggregate(toplam=Sum('toplam_fiyat'))['toplam']
        self.toplam_gelir = toplam_gelir or 0

        toplam_odenen = siparisler.aggregate(toplam=Sum('odenen_miktar'))['toplam']
        self.toplam_odenen = toplam_odenen or 0

    def kalan_tahsilat(self):
        """Rapor dönemindeki kalan tahsilat miktarını hesaplar"""
        return self.toplam_gelir - self.toplam_odenen

    def tahsilat_orani(self):
        """Rapor dönemindeki tahsilat oranını hesaplar (%)"""
        if self.toplam_gelir > 0:
            return (float(self.toplam_odenen) / self.toplam_gelir) * 100
        return 0
