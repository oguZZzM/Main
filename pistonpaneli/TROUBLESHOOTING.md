# Piston Paneli - Sorun Giderme Kılavuzu

Bu belge, Piston Paneli projesinde karşılaşılabilecek yaygın sorunları ve çözümlerini içerir.

## Kurulum Sorunları

### ModuleNotFoundError: Çeşitli Modüller

Aşağıdaki modüllerle ilgili hatalar alabilirsiniz:

#### Veri Dışa Aktarma Araçları

Bu hata, özel geliştirdiğimiz veri dışa aktarma araçlarının yüklü olmadığını gösterir. Çözmek için:

```bash
pip install -r requirements.txt
```

veya doğrudan:

```bash
pip install data-export-tools
```

#### PDF Oluşturma Araçları

Bu hata, PDF oluşturma araçlarının yüklü olmadığını gösterir. Çözmek için:

```bash
pip install -r requirements.txt
```

veya doğrudan:

```bash
pip install WeasyPrint reportlab pillow
```

## Veritabanı Sorunları

### Veritabanı Tabloları Bulunamadı

Bu sorun, veritabanı şemasının oluşturulmadığını gösterir. Çözmek için:

```bash
python setup.py initialize_db
```

### Veritabanı Şema Değişiklikleri

Veri modellerinde yapılan değişiklikler sonrasında veritabanı şemasını güncellemek için:

```bash
python setup.py update_schema
python setup.py apply_schema
```

## Çalıştırma Sorunları

### Sunucu Başlatılamıyor

Sunucuyu başlatırken hata alıyorsanız, önce bağımlılıkların yüklü olduğundan emin olun:

```bash
pip install -r requirements.txt
```

Ardından, projenin yapılandırmasını kontrol edin:

```bash
python setup.py verify_config
```

Sorun devam ederse, hata mesajını inceleyerek sorunu belirlemeye çalışın.

## Genel Sorun Giderme Adımları

1. Tüm bağımlılıkların yüklü olduğundan emin olun:
   ```bash
   pip install -r requirements.txt
   ```

2. Veritabanı şemasının güncel olduğundan emin olun:
   ```bash
   python setup.py repair_db
   ```

3. Proje yapılandırmasını kontrol edin:
   ```bash
   python setup.py verify_config
   ```

4. Statik dosyaları toplayın:
   ```bash
   python setup.py collect_assets
   ```

5. Uygulamayı başlatın:
   ```bash
   python run.py
   ```

## Yardım ve Destek

Daha fazla yardıma ihtiyacınız varsa veya bu belgede ele alınmayan bir sorunla karşılaşırsanız, lütfen proje yöneticisiyle iletişime geçin.
