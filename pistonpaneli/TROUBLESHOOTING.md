# Piston Paneli - Sorun Giderme Kılavuzu

Bu belge, Piston Paneli projesinde karşılaşılabilecek yaygın sorunları ve çözümlerini içerir.

## Kurulum Sorunları

### ModuleNotFoundError: No module named 'import_export'

Bu hata, `django-import-export` paketinin yüklü olmadığını gösterir. Çözmek için:

```bash
pip install -r requirements.txt
```

veya doğrudan:

```bash
pip install django-import-export
```

### ModuleNotFoundError: No module named 'django_extensions'

Bu hata, `django-extensions` paketinin yüklü olmadığını gösterir. Çözmek için:

```bash
pip install -r requirements.txt
```

veya doğrudan:

```bash
pip install django-extensions
```

### ModuleNotFoundError: No module named 'weasyprint'

Bu hata, `WeasyPrint` paketinin yüklü olmadığını gösterir. Çözmek için:

```bash
pip install -r requirements.txt
```

veya doğrudan:

```bash
pip install WeasyPrint
```

## Veritabanı Sorunları

### Veritabanı Tabloları Bulunamadı

Bu sorun, veritabanı migrasyonlarının uygulanmadığını gösterir. Çözmek için:

```bash
python manage.py migrate
```

### Veritabanı Şema Değişiklikleri

Modellerde yapılan değişiklikler sonrasında veritabanı şemasını güncellemek için:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Çalıştırma Sorunları

### Sunucu Başlatılamıyor

Sunucuyu başlatırken hata alıyorsanız, önce bağımlılıkların yüklü olduğundan emin olun:

```bash
pip install -r requirements.txt
```

Ardından, projenin yapılandırmasını kontrol edin:

```bash
python manage.py check
```

Sorun devam ederse, hata mesajını inceleyerek sorunu belirlemeye çalışın.

## Genel Sorun Giderme Adımları

1. Tüm bağımlılıkların yüklü olduğundan emin olun:
   ```bash
   pip install -r requirements.txt
   ```

2. Veritabanı migrasyonlarının uygulandığından emin olun:
   ```bash
   python manage.py migrate
   ```

3. Proje yapılandırmasını kontrol edin:
   ```bash
   python manage.py check
   ```

4. Statik dosyaları toplayın:
   ```bash
   python manage.py collectstatic
   ```

5. Geliştirme sunucusunu başlatın:
   ```bash
   python manage.py runserver
   ```

## Yardım ve Destek

Daha fazla yardıma ihtiyacınız varsa veya bu belgede ele alınmayan bir sorunla karşılaşırsanız, lütfen proje yöneticisiyle iletişime geçin.