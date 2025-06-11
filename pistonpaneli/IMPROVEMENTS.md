# Piston Paneli - İyileştirmeler Dokümantasyonu

Bu belge, Piston Paneli projesinin işlevselliğini ve kullanıcı deneyimini geliştirmek için yapılan iyileştirmeleri açıklar.

## 1. Veri Dışa Aktarma İşlevi

### Açıklama
Django Import-Export paketi kullanılarak tüm ana modellerden verileri çeşitli formatlarda (CSV, Excel, JSON, vb.) dışa aktarma yeteneği eklendi.

### Uygulama Detayları
- Proje bağımlılıklarına `django-import-export` eklendi
- Her model için `siparis/resources.py` içinde kaynak sınıfları oluşturuldu
- Admin sınıfları bu kaynakları kullanacak şekilde güncellendi
- Her model için dışa aktarma formatları ve alanları yapılandırıldı

### Kullanım
1. Herhangi bir admin liste görünümüne gidin (Siparişler, Müşteriler, vb.)
2. Sağ üst köşedeki "Dışa Aktar" düğmesini arayın
3. İstediğiniz formatı seçin ve "Dışa Aktar" düğmesine tıklayın

## 2. PDF Oluşturma

### Açıklama
WeasyPrint kullanarak faturalar ve raporlar için PDF belgeleri oluşturma yeteneği eklendi.

### Uygulama Detayları
- Proje bağımlılıklarına `WeasyPrint` eklendi
- `siparis/templates/` içinde PDF şablonları oluşturuldu
  - Sipariş faturaları için `invoice_pdf.html`
  - Raporlar için `report_pdf.html`
- `siparis/utils.py` içinde PDF oluşturma yardımcı programları uygulandı
- PDF oluşturma için görünümler ve URL'ler eklendi
- Sipariş ve rapor detay sayfalarına PDF indirme düğmeleri eklendi

### Kullanım
- **Sipariş Faturaları**: Sipariş detay sayfasında "Fatura PDF" düğmesine tıklayın
- **Raporlar**: Rapor detay sayfasında "PDF İndir" düğmesine tıklayın

## 3. E-posta Bildirimleri

### Açıklama
Sistemdeki önemli olaylar için bir e-posta bildirim sistemi uygulandı:
- Sipariş durumu değişiklikleri
- Ödeme makbuzları
- Kritik stok uyarıları

### Uygulama Detayları
- `settings.py` içinde e-posta ayarları yapılandırıldı
- `siparis/utils.py` içinde e-posta yardımcı işlevleri uygulandı
- Modeller, belirli olaylarda bildirim gönderecek şekilde değiştirildi:
  - `Siparis.save()`: Sipariş durumu değiştiğinde bildirimler gönderir
  - `Odeme.save()`: Yeni ödemeler kaydedildiğinde bildirimler gönderir
  - `Malzeme.save()` ve `Malzeme.stok_cikar()`: Stok minimum seviyenin altına düştüğünde uyarılar gönderir

### Yapılandırma
E-posta ayarları `settings.py` içinde yapılandırılabilir:
```python
# E-posta ayarları
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.example.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-password'

# Varsayılan e-posta ayarları
DEFAULT_FROM_EMAIL = 'pistonpaneli@example.com'
ADMIN_EMAIL = 'admin@example.com'
```

Geliştirme için, konsolda e-postaları görmek üzere konsol backend'ini kullanabilirsiniz:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Test
E-posta bildirimlerini doğrulamak için bir test betiği sağlanmıştır:
```bash
python manage.py test_email_notifications
```

## 4. Tam Sayı Alanı Dönüşümü

### Açıklama
Daha iyi performans ve daha basit görüntüleme için ondalık alanlar tam sayı alanlarına dönüştürüldü.

### Uygulama Detayları
- `siparis/models.py` içindeki model alanları `DecimalField` yerine `IntegerField` kullanacak şekilde değiştirildi
- Mevcut ondalık değerleri tam sayılara dönüştürmek için bir veri geçiş betiği oluşturuldu
- İlgili kod, tam sayı değerlerini işleyecek şekilde güncellendi

### Test
Tam sayı alanı dönüşümünü doğrulamak için bir test betiği sağlanmıştır:
```bash
python manage.py test_integer_fields
```

## 5. Geliştirilmiş Rapor Görüntüleme

### Açıklama
Raporlardaki tahsilat oranlarının görüntülenmesi, daha iyi biçimlendirme ve görsel göstergelerle geliştirildi.

### Uygulama Detayları
- `RaporAdmin` sınıfındaki `tahsilat_orani_yuzde` metodu güncellendi
- Tahsilat oranı yüzdesine dayalı renk kodlaması eklendi
- Yüzdenin altına ödeme bilgileri görüntüleme eklendi

## Yeni Bağımlılıkların Kurulumu

Yeni bağımlılıkları kurmak için şunu çalıştırın:
```bash
pip install -r requirements.txt
```

Veya bunları ayrı ayrı kurun:
```bash
pip install django-import-export WeasyPrint django-extensions
```
