from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Sipariş URL'leri
    path('siparisler/', views.siparisler_listesi, name='siparisler_listesi'),
    path('siparis/ekle/', views.siparis_ekle, name='siparis_ekle'),
    path('siparis/duzenle/<int:siparis_id>/', views.siparis_duzenle, name='siparis_duzenle'),
    path('siparis/detay/<int:siparis_id>/', views.siparis_detay, name='siparis_detay'),
    path('siparis/sil/<int:siparis_id>/', views.siparis_sil, name='siparis_sil_onay'),
    path('siparis/<int:siparis_id>/odeme/ekle/', views.odeme_ekle, name='odeme_ekle'),
    path('siparis/<int:siparis_id>/malzeme/ekle/', views.malzeme_ekle, name='malzeme_ekle'),

    # Müşteri URL'leri
    path('musteriler/', views.musteriler_listesi, name='musteriler_listesi'),
    path('musteri/ekle/', views.musteri_ekle, name='musteri_ekle'),
    path('musteri/duzenle/<int:musteri_id>/', views.musteri_duzenle, name='musteri_duzenle'),
    path('musteri/sil/<int:musteri_id>/', views.musteri_sil, name='musteri_sil_onay'),

    # Malzeme URL'leri
    path('malzemeler/', views.malzemeler_listesi, name='malzemeler_listesi'),
    path('malzeme/ekle/', views.malzeme_duzenle, name='malzeme_ekle'),
    path('malzeme/detay/<int:malzeme_id>/', views.malzeme_detay, name='malzeme_detay'),
    path('malzeme/duzenle/<int:malzeme_id>/', views.malzeme_duzenle, name='malzeme_duzenle'),
    path('malzeme/sil/<int:malzeme_id>/', views.malzeme_sil, name='malzeme_sil'),

    # Malzeme Kullanımı URL'leri
    path('malzeme-kullanimlari/', views.malzeme_kullanimi_listesi, name='malzeme_kullanimi_listesi'),

    # Rapor URL'leri
    path('raporlar/', views.raporlar_listesi, name='raporlar_listesi'),
    path('rapor/olustur/', views.rapor_olustur, name='rapor_olustur'),
    path('rapor/detay/<int:rapor_id>/', views.rapor_detay, name='rapor_detay'),
    path('rapor/sil/<int:rapor_id>/', views.rapor_sil, name='rapor_sil'),

    # Ödeme URL'leri
    path('odemeler/', views.odemeler_listesi, name='odemeler_listesi'),

    # Grafik URL'leri
    path('grafik/', views.grafik_sayfasi, name='grafik_sayfasi'),

    # PDF URL'leri
    path('siparis/<int:siparis_id>/pdf/', views.siparis_pdf, name='siparis_pdf'),
    path('rapor/<int:rapor_id>/pdf/', views.rapor_pdf, name='rapor_pdf'),
]
