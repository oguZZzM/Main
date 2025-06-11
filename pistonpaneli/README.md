# Piston Paneli

Piston Paneli, özellikle piston ve hidrolik silindir endüstrisindeki üretim işletmeleri için tasarlanmış kapsamlı bir sipariş ve envanter yönetim sistemidir.

## Kurulum

### Ön Koşullar

- Python 3.8 veya daha yüksek
- pip (Python paket yöneticisi)
- Sanal ortam (önerilir)

### Kurulum Adımları

1. Depoyu klonlayın:
```bash
git clone <repository-url>
cd pistonpaneli
```

2. Sanal ortam oluşturun ve etkinleştirin (önerilir):
```bash
python -m venv venv
source venv/bin/activate  # Windows'ta: venv\Scripts\activate
```

3. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

4. Migrasyonları uygulayın:
```bash
python manage.py migrate
```

5. Bir süper kullanıcı oluşturun:
```bash
python manage.py createsuperuser
```

6. Geliştirme sunucusunu çalıştırın:
```bash
python manage.py runserver
```

7. Admin arayüzüne http://127.0.0.1:8000/admin/ adresinden erişin

## Sorun Giderme

Yaygın sorunlar ve çözümleri için lütfen [Sorun Giderme Kılavuzu](TROUBLESHOOTING.md)'na bakın.

Yaygın sorunlar şunları içerir:
- Eksik bağımlılıklar (import_export, django_extensions, weasyprint)
- Veritabanı migrasyon sorunları
- Sunucu başlatma sorunları

Çoğu sorun için hızlı çözüm:
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
```

## Özellikler

- Müşteri yönetimi
- Sipariş takibi
- Ödeme takibi
- Envanter yönetimi
- Malzeme kullanımı takibi
- Raporlama
- Faturalar ve raporlar için PDF oluşturma
- Önemli olaylar için e-posta bildirimleri
- Çeşitli formatlarda veri dışa aktarma (CSV, Excel, JSON, vb.)

## Dokümantasyon

- [IMPROVEMENTS.md](IMPROVEMENTS.md) - Projeye yapılan iyileştirmeler hakkında detaylı bilgi
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Yaygın sorunları çözme kılavuzu
- [CHANGES.md](CHANGES.md) - Değişiklikler ve düzeltilen sorunların günlüğü

## Lisans

Bu proje MIT Lisansı altında lisanslanmıştır - detaylar için LICENSE dosyasına bakın.
