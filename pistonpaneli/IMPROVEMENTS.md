# Piston Paneli - İyileştirmeler Dokümantasyonu

Bu belge, Piston Paneli projesinin işlevselliğini ve kullanıcı deneyimini geliştirmek için yapılan iyileştirmeleri açıklar.

## 1. Yönetim Paneli Geliştirme Süreci

### Tasarım Yaklaşımı
Piston Paneli'nin yönetim arayüzü, kullanıcı deneyimini ön planda tutan bir yaklaşımla sıfırdan tasarlandı. Temel hedeflerimiz şunlardı:
- Sezgisel ve kullanımı kolay bir arayüz
- Görsel olarak çekici ve modern bir tasarım
- Mobil cihazlarda da sorunsuz çalışan duyarlı (responsive) bir yapı
- Hızlı erişim için optimize edilmiş navigasyon

### Teknoloji Seçimleri
Yönetim panelini geliştirirken şu teknolojileri kullandık:
- HTML5 ve CSS3 (modern web standartları)
- JavaScript ve jQuery (etkileşimli öğeler için)
- Bootstrap (duyarlı tasarım için)
- Font Awesome (ikonlar için)
- WeasyPrint (PDF oluşturma için)
- Özel CSS ve JavaScript kütüphaneleri

### Özelleştirme Süreci
Yönetim panelini özelleştirmek için aşağıdaki adımları izledik:

1. **Temel Yapı Oluşturma**:
   - Temel HTML şablonları tasarlandı
   - Sayfa düzeni ve grid sistemi oluşturuldu
   - Ana navigasyon yapısı belirlendi

2. **Görsel Kimlik Entegrasyonu**:
   - Piston Paneli logosu ve renk şeması uygulandı
   - Tutarlı tipografi ve görsel öğeler eklendi
   - Özel ikonlar ve görsel varlıklar entegre edildi

3. **Kullanıcı Arayüzü Bileşenleri**:
   - Özel form elemanları tasarlandı
   - Veri tabloları ve liste görünümleri geliştirildi
   - Bildirim sistemi ve uyarı mesajları oluşturuldu
   - Dashboard widget'ları ve grafikler eklendi

4. **Performans Optimizasyonu**:
   - CSS ve JavaScript dosyaları minimize edildi
   - Görsel varlıklar optimize edildi
   - Sayfa yükleme süreleri iyileştirildi

### Özel Bileşenler
Yönetim panelimiz için geliştirdiğimiz bazı özel bileşenler:

- **Özelleştirilmiş Dashboard**: Kullanıcıların en önemli bilgileri tek bir bakışta görebilecekleri bir dashboard
- **Gelişmiş Veri Tabloları**: Sıralama, filtreleme ve arama özellikleriyle donatılmış veri tabloları
- **Sezgisel Formlar**: Kullanıcı dostu, doğrulama özellikli formlar
- **Bildirim Sistemi**: Önemli olaylar için gerçek zamanlı bildirimler
- **Tema Desteği**: Açık/koyu mod ve özelleştirilebilir renk şemaları

### Sonuç
Geliştirdiğimiz yönetim paneli, kullanıcıların Piston Paneli'nin tüm özelliklerine kolayca erişmesini sağlayan, görsel açıdan çekici ve kullanımı kolay bir arayüz sunuyor. Sürekli geri bildirimler doğrultusunda iyileştirmeler yapmaya devam ediyoruz.

## 2. Veri Dışa Aktarma İşlevi

### Açıklama
Özel geliştirdiğimiz veri dışa aktarma modülü kullanılarak tüm ana modellerden verileri çeşitli formatlarda (CSV, Excel, JSON, vb.) dışa aktarma yeteneği eklendi.

### Uygulama Detayları
- Proje bağımlılıklarına `data-export-tools` eklendi
- Her model için `siparis/resources.py` içinde özel kaynak sınıfları oluşturuldu
- Yönetim paneli sınıfları bu kaynakları kullanacak şekilde güncellendi
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
- `config.py` içinde e-posta ayarları yapılandırıldı
- `siparis/utils.py` içinde e-posta yardımcı işlevleri uygulandı
- Veri modelleri, belirli olaylarda bildirim gönderecek şekilde değiştirildi:
  - `Siparis.kaydet()`: Sipariş durumu değiştiğinde bildirimler gönderir
  - `Odeme.kaydet()`: Yeni ödemeler kaydedildiğinde bildirimler gönderir
  - `Malzeme.kaydet()` ve `Malzeme.stok_cikar()`: Stok minimum seviyenin altına düştüğünde uyarılar gönderir

### Yapılandırma
E-posta ayarları `config.py` içinde yapılandırılabilir:
```python
# E-posta ayarları
EMAIL_BACKEND = 'piston.mail.smtp.SMTPBackend'
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
EMAIL_BACKEND = 'piston.mail.console.ConsoleBackend'
```

### Test
E-posta bildirimlerini doğrulamak için bir test betiği sağlanmıştır:
```bash
python setup.py test_email_notifications
```

## 4. Tam Sayı Alanı Dönüşümü

### Açıklama
Daha iyi performans ve daha basit görüntüleme için ondalık alanlar tam sayı alanlarına dönüştürüldü.

### Uygulama Detayları
- `siparis/models.py` içindeki veri modeli alanları `OndalikAlan` yerine `TamSayiAlan` kullanacak şekilde değiştirildi
- Mevcut ondalık değerleri tam sayılara dönüştürmek için bir veri geçiş betiği oluşturuldu
- İlgili kod, tam sayı değerlerini işleyecek şekilde güncellendi

### Test
Tam sayı alanı dönüşümünü doğrulamak için bir test betiği sağlanmıştır:
```bash
python setup.py test_integer_fields
```

## 5. Geliştirilmiş Rapor Görüntüleme

### Açıklama
Raporlardaki tahsilat oranlarının görüntülenmesi, daha iyi biçimlendirme ve görsel göstergelerle geliştirildi.

### Uygulama Detayları
- `RaporYonetici` sınıfındaki `tahsilat_orani_yuzde` metodu güncellendi
- Tahsilat oranı yüzdesine dayalı renk kodlaması eklendi
- Yüzdenin altına ödeme bilgileri görüntüleme eklendi

## Yeni Bağımlılıkların Kurulumu

Yeni bağımlılıkları kurmak için şunu çalıştırın:
```bash
pip install -r requirements.txt
```

Veya bunları ayrı ayrı kurun:
```bash
pip install data-export-tools WeasyPrint reportlab pillow
```
