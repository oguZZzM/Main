from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from import_export.admin import ImportExportModelAdmin
from .models import Musteri, Siparis, Odeme, Malzeme, MalzemeKullanimi, Rapor
from .resources import MusteriResource, SiparisResource, OdemeResource, MalzemeResource, MalzemeKullanimiResource, RaporResource

class OdemeInline(admin.TabularInline):
    model = Odeme
    extra = 0
    readonly_fields = ('tarih',)
    fields = ('tarih', 'miktar', 'aciklama')

class MalzemeKullanimiInline(admin.TabularInline):
    model = MalzemeKullanimi
    extra = 0
    readonly_fields = ('tarih', 'toplam_deger')
    fields = ('malzeme', 'miktar', 'aciklama', 'tarih', 'toplam_deger')
    autocomplete_fields = ['malzeme']

@admin.register(Siparis)
class SiparisAdmin(ImportExportModelAdmin):
    resource_class = SiparisResource
    list_display = ('musteri', 'urun_tipi', 'adet', 'iscilik_turu', 'tarih', 'durum_renkli', 
                   'birim_fiyat', 'toplam_fiyat', 'odeme_durumu_renkli', 'odenen_miktar', 'siparis_yasi')
    list_filter = ('durum', 'iscilik_turu', 'tarih', 'odeme_durumu', 'oncelik')
    search_fields = ('urun_tipi', 'aciklama', 'musteri__isim', 'musteri__firmasi')
    readonly_fields = ('toplam_fiyat', 'odeme_durumu', 'tarih', 'siparis_yasi', 'gecikme_suresi', 'kalan_odeme')
    autocomplete_fields = ['musteri']
    list_per_page = 25
    date_hierarchy = 'tarih'
    list_select_related = ['musteri']
    show_full_result_count = True
    save_on_top = True
    actions = ['mark_as_completed', 'mark_as_delivered', 'mark_as_paid']

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(durum='tamamlandi')
        self.message_user(request, f'{updated} sipariş tamamlandı olarak işaretlendi.')
    mark_as_completed.short_description = "Seçili siparişleri tamamlandı olarak işaretle"

    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(durum='teslim_edildi')
        self.message_user(request, f'{updated} sipariş teslim edildi olarak işaretlendi.')
    mark_as_delivered.short_description = "Seçili siparişleri teslim edildi olarak işaretle"

    def mark_as_paid(self, request, queryset):
        updated = queryset.update(odeme_durumu='odendi')
        self.message_user(request, f'{updated} sipariş ödendi olarak işaretlendi.')
    mark_as_paid.short_description = "Seçili siparişleri ödendi olarak işaretle"

    fieldsets = (
        ('Müşteri Bilgileri', {
            'fields': ('musteri',)
        }),
        ('Sipariş Detayları', {
            'fields': ('urun_tipi', 'adet', 'iscilik_turu', 'aciklama', 'oncelik')
        }),
        ('Durum Bilgileri', {
            'fields': ('durum', 'tarih', 'teslim_tarihi', 'siparis_yasi', 'gecikme_suresi')
        }),
        ('Ödeme Bilgileri', {
            'fields': ('birim_fiyat', 'toplam_fiyat', 'odeme_durumu', 'odenen_miktar', 'kalan_odeme')
        }),
    )
    inlines = [OdemeInline, MalzemeKullanimiInline]

    def durum_renkli(self, obj):
        """Durumu renkli göster"""
        renk_map = {
            'beklemede': 'blue',
            'uretimde': 'orange',
            'tamamlandi': 'green',
            'teslim_edildi': 'purple',
            'iptal_edildi': 'red',
        }
        renk = renk_map.get(obj.durum, 'black')
        durum_text = obj.get_durum_display() if hasattr(obj, 'get_durum_display') else obj.durum
        return format_html('<span style="color: {};">{}</span>', renk, durum_text)
    durum_renkli.short_description = 'Durum'
    durum_renkli.admin_order_field = 'durum'

    def odeme_durumu_renkli(self, obj):
        """Ödeme durumunu renkli göster"""
        renk_map = {
            'odenmedi': 'red',
            'kismi_odendi': 'orange',
            'odendi': 'green',
        }
        renk = renk_map.get(obj.odeme_durumu, 'black')
        odeme_durumu_text = obj.get_odeme_durumu_display() if hasattr(obj, 'get_odeme_durumu_display') else obj.odeme_durumu
        return format_html('<span style="color: {};">{}</span>', renk, odeme_durumu_text)
    odeme_durumu_renkli.short_description = 'Ödeme Durumu'
    odeme_durumu_renkli.admin_order_field = 'odeme_durumu'

@admin.register(Musteri)
class MusteriAdmin(ImportExportModelAdmin):
    resource_class = MusteriResource
    list_display = ('isim', 'firmasi', 'telefon', 'kayit_tarihi', 'toplam_siparis_sayisi', 'toplam_borc', 'odenen_miktar', 'kalan_borc')
    search_fields = ('isim', 'firmasi', 'telefon')
    list_filter = ('firmasi', 'kayit_tarihi')
    readonly_fields = ('kayit_tarihi', 'toplam_siparis_sayisi', 'toplam_borc', 'odenen_miktar', 'kalan_borc')
    list_per_page = 25
    show_full_result_count = True
    save_on_top = True
    actions = ['export_customer_data', 'mark_as_vip']

    def export_customer_data(self, request, queryset):
        # This is a placeholder for the export functionality
        # In a real implementation, you would generate and return a file
        self.message_user(request, f'{queryset.count()} müşteri verisi dışa aktarıldı.')
    export_customer_data.short_description = "Seçili müşterilerin verilerini dışa aktar"

    def mark_as_vip(self, request, queryset):
        # This is a placeholder for VIP marking functionality
        # In a real implementation, you would set a VIP flag on the customer model
        self.message_user(request, f'{queryset.count()} müşteri VIP olarak işaretlendi.')
    mark_as_vip.short_description = "Seçili müşterileri VIP olarak işaretle"

    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('isim', 'firmasi', 'telefon', 'adres', 'kayit_tarihi'),
            'classes': ('wide',)
        }),
        ('Sipariş İstatistikleri', {
            'fields': ('toplam_siparis_sayisi', 'toplam_borc', 'odenen_miktar', 'kalan_borc'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Odeme)
class OdemeAdmin(ImportExportModelAdmin):
    resource_class = OdemeResource
    list_display = ('siparis', 'tarih', 'miktar', 'aciklama')
    list_filter = ('tarih',)
    search_fields = ('siparis__musteri__isim', 'siparis__urun_tipi', 'aciklama')
    date_hierarchy = 'tarih'
    autocomplete_fields = ['siparis']
    readonly_fields = ('tarih',)

@admin.register(Malzeme)
class MalzemeAdmin(ImportExportModelAdmin):
    resource_class = MalzemeResource
    list_display = ('ad', 'tur', 'stok_miktari', 'birim', 'birim_fiyat', 'toplam_deger', 'stok_durumu', 'son_guncelleme')
    search_fields = ('ad', 'aciklama')
    list_filter = ('tur', 'birim', 'son_guncelleme')
    readonly_fields = ('son_guncelleme', 'toplam_deger')
    list_per_page = 25
    show_full_result_count = True
    save_on_top = True
    actions = ['restock_materials', 'mark_as_critical']

    def restock_materials(self, request, queryset):
        # This is a placeholder for restocking functionality
        # In a real implementation, you would increase stock levels
        self.message_user(request, f'{queryset.count()} malzeme stoku yenilendi.')
    restock_materials.short_description = "Seçili malzemelerin stokunu yenile"

    def mark_as_critical(self, request, queryset):
        # This is a placeholder for marking materials as critical
        # In a real implementation, you would set minimum_stok to current stok_miktari
        for material in queryset:
            material.minimum_stok = material.stok_miktari
            material.save()
        self.message_user(request, f'{queryset.count()} malzeme kritik olarak işaretlendi.')
    mark_as_critical.short_description = "Seçili malzemeleri kritik olarak işaretle"

    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('ad', 'tur', 'aciklama'),
            'classes': ('wide',)
        }),
        ('Stok Bilgileri', {
            'fields': ('stok_miktari', 'birim', 'minimum_stok', 'birim_fiyat', 'toplam_deger', 'son_guncelleme'),
            'description': 'Stok miktarı ve fiyat bilgileri. Minimum stok seviyesi, stok durumunun kritik olarak işaretlenmesi için kullanılır.'
        }),
    )

    def stok_durumu(self, obj):
        """Stok durumunu renkli göster"""
        try:
            if obj.stok_miktari <= 0:
                return format_html('<span style="color: red; font-weight: bold;">Stokta Yok</span>')
            elif hasattr(obj, 'stok_durumu_kritik_mi') and obj.stok_durumu_kritik_mi():
                return format_html('<span style="color: orange; font-weight: bold;">Kritik</span>')
            elif hasattr(obj, 'minimum_stok') and obj.stok_miktari <= obj.minimum_stok:
                # stok_durumu_kritik_mi metodu yoksa yedek kontrol
                return format_html('<span style="color: orange; font-weight: bold;">Kritik</span>')
            else:
                return format_html('<span style="color: green;">Yeterli</span>')
        except Exception as e:
            # Herhangi bir hata olursa varsayılan değer döndür
            return format_html('<span style="color: gray;">Bilinmiyor</span>')
    stok_durumu.short_description = 'Stok Durumu'

@admin.register(MalzemeKullanimi)
class MalzemeKullanimiAdmin(ImportExportModelAdmin):
    resource_class = MalzemeKullanimiResource
    list_display = ('siparis', 'malzeme', 'miktar', 'toplam_deger', 'tarih', 'aciklama')
    list_filter = ('tarih', 'malzeme__tur')
    search_fields = ('siparis__musteri__isim', 'malzeme__ad', 'aciklama')
    date_hierarchy = 'tarih'
    autocomplete_fields = ['siparis', 'malzeme']
    readonly_fields = ('tarih', 'toplam_deger')

@admin.register(Rapor)
class RaporAdmin(ImportExportModelAdmin):
    resource_class = RaporResource
    list_display = ('baslik', 'tip', 'baslangic_tarihi', 'bitis_tarihi', 'toplam_siparis', 'toplam_gelir', 'toplam_odenen', 'tahsilat_orani_yuzde')
    list_filter = ('tip', 'olusturulma_tarihi')
    search_fields = ('baslik', 'aciklama')
    date_hierarchy = 'olusturulma_tarihi'
    readonly_fields = ('olusturulma_tarihi', 'kalan_tahsilat', 'tahsilat_orani_yuzde')

    fieldsets = (
        ('Rapor Bilgileri', {
            'fields': ('baslik', 'tip', 'baslangic_tarihi', 'bitis_tarihi', 'aciklama', 'olusturulma_tarihi')
        }),
        ('İstatistikler', {
            'fields': ('toplam_siparis', 'toplam_gelir', 'toplam_odenen', 'kalan_tahsilat', 'tahsilat_orani_yuzde')
        }),
    )

    def tahsilat_orani_yuzde(self, obj):
        """Tahsilat oranını yüzde olarak göster"""
        try:
            # Tahsilat oranını hesapla
            if hasattr(obj, 'tahsilat_orani'):
                oran = obj.tahsilat_orani()
            else:
                # Metod yoksa yedek hesaplama
                if obj.toplam_gelir > 0:
                    oran = (float(obj.toplam_odenen) / obj.toplam_gelir) * 100
                else:
                    oran = 0

            # Oran formatını önceden hazırla
            oran_str = f"%{oran:.2f}"

            # Ödeme bilgisini hazırla
            try:
                odeme_bilgisi = f"{obj.toplam_odenen:,} / {obj.toplam_gelir:,} TL"
            except:
                odeme_bilgisi = f"{obj.toplam_odenen} / {obj.toplam_gelir} TL"

            # Renk ve stil belirle
            if oran >= 90:
                renk = 'green'
                stil = 'font-weight: bold;'
            elif oran >= 50:
                renk = 'orange'
                stil = 'font-weight: bold;'
            else:
                renk = 'red'
                stil = ''

            # HTML oluştur
            return format_html(
                '<div><span style="color: {}; {}">{}</span><br/>'
                '<span style="font-size: 0.8em; color: #666;">{}</span></div>', 
                renk, stil, oran_str, odeme_bilgisi
            )
        except Exception as e:
            # Herhangi bir hata olursa varsayılan değer döndür
            return format_html('<span style="color: gray;">%0.00</span>')
    tahsilat_orani_yuzde.short_description = 'Tahsilat Oranı'

    def kalan_tahsilat(self, obj):
        """Kalan tahsilat miktarını göster"""
        try:
            if hasattr(obj, 'kalan_tahsilat'):
                return obj.kalan_tahsilat()
            else:
                # Metod yoksa yedek hesaplama
                return obj.toplam_gelir - obj.toplam_odenen
        except Exception as e:
            # Herhangi bir hata olursa varsayılan değer döndür
            return 0
    kalan_tahsilat.short_description = 'Kalan Tahsilat (TL)'


