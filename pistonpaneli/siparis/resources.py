from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Musteri, Siparis, Odeme, Malzeme, MalzemeKullanimi, Rapor

class MusteriResource(resources.ModelResource):
    """Resource for exporting Musteri model data"""
    class Meta:
        model = Musteri
        fields = ('id', 'isim', 'firmasi', 'telefon', 'adres', 'kayit_tarihi')
        export_order = ('id', 'isim', 'firmasi', 'telefon', 'adres', 'kayit_tarihi')

class SiparisResource(resources.ModelResource):
    """Resource for exporting Siparis model data"""
    musteri = fields.Field(
        column_name='musteri',
        attribute='musteri',
        widget=ForeignKeyWidget(Musteri, 'isim')
    )
    durum_display = fields.Field(
        column_name='durum_display',
        attribute='get_durum_display'
    )
    iscilik_turu_display = fields.Field(
        column_name='iscilik_turu_display',
        attribute='get_iscilik_turu_display'
    )
    odeme_durumu_display = fields.Field(
        column_name='odeme_durumu_display',
        attribute='get_odeme_durumu_display'
    )
    
    class Meta:
        model = Siparis
        fields = (
            'id', 'musteri', 'urun_tipi', 'adet', 'iscilik_turu', 'iscilik_turu_display',
            'tarih', 'teslim_tarihi', 'durum', 'durum_display', 'aciklama', 
            'birim_fiyat', 'toplam_fiyat', 'odeme_durumu', 'odeme_durumu_display', 
            'odenen_miktar', 'oncelik'
        )
        export_order = (
            'id', 'musteri', 'urun_tipi', 'adet', 'iscilik_turu', 'iscilik_turu_display',
            'tarih', 'teslim_tarihi', 'durum', 'durum_display', 'aciklama', 
            'birim_fiyat', 'toplam_fiyat', 'odeme_durumu', 'odeme_durumu_display', 
            'odenen_miktar', 'oncelik'
        )

class OdemeResource(resources.ModelResource):
    """Resource for exporting Odeme model data"""
    siparis = fields.Field(
        column_name='siparis',
        attribute='siparis',
        widget=ForeignKeyWidget(Siparis, 'urun_tipi')
    )
    musteri = fields.Field(
        column_name='musteri',
        attribute='siparis__musteri',
        widget=ForeignKeyWidget(Musteri, 'isim')
    )
    
    class Meta:
        model = Odeme
        fields = ('id', 'siparis', 'musteri', 'tarih', 'miktar', 'aciklama')
        export_order = ('id', 'siparis', 'musteri', 'tarih', 'miktar', 'aciklama')

class MalzemeResource(resources.ModelResource):
    """Resource for exporting Malzeme model data"""
    tur_display = fields.Field(
        column_name='tur_display',
        attribute='get_tur_display'
    )
    birim_display = fields.Field(
        column_name='birim_display',
        attribute='get_birim_display'
    )
    
    class Meta:
        model = Malzeme
        fields = (
            'id', 'ad', 'tur', 'tur_display', 'stok_miktari', 'birim', 
            'birim_display', 'birim_fiyat', 'aciklama', 'son_guncelleme', 
            'minimum_stok'
        )
        export_order = (
            'id', 'ad', 'tur', 'tur_display', 'stok_miktari', 'birim', 
            'birim_display', 'birim_fiyat', 'aciklama', 'son_guncelleme', 
            'minimum_stok'
        )

class MalzemeKullanimiResource(resources.ModelResource):
    """Resource for exporting MalzemeKullanimi model data"""
    siparis = fields.Field(
        column_name='siparis',
        attribute='siparis',
        widget=ForeignKeyWidget(Siparis, 'urun_tipi')
    )
    malzeme = fields.Field(
        column_name='malzeme',
        attribute='malzeme',
        widget=ForeignKeyWidget(Malzeme, 'ad')
    )
    
    class Meta:
        model = MalzemeKullanimi
        fields = ('id', 'siparis', 'malzeme', 'miktar', 'tarih', 'aciklama')
        export_order = ('id', 'siparis', 'malzeme', 'miktar', 'tarih', 'aciklama')

class RaporResource(resources.ModelResource):
    """Resource for exporting Rapor model data"""
    tip_display = fields.Field(
        column_name='tip_display',
        attribute='get_tip_display'
    )
    
    class Meta:
        model = Rapor
        fields = (
            'id', 'baslik', 'tip', 'tip_display', 'baslangic_tarihi', 'bitis_tarihi',
            'olusturulma_tarihi', 'toplam_siparis', 'toplam_gelir', 'toplam_odenen',
            'aciklama'
        )
        export_order = (
            'id', 'baslik', 'tip', 'tip_display', 'baslangic_tarihi', 'bitis_tarihi',
            'olusturulma_tarihi', 'toplam_siparis', 'toplam_gelir', 'toplam_odenen',
            'aciklama'
        )