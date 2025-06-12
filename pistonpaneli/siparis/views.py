from django.db.models import Count, Sum
from django.shortcuts import render, redirect, get_object_or_404
from .models import Musteri, Siparis, Odeme, Malzeme, MalzemeKullanimi, Rapor
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from decimal import Decimal
from .utils import generate_invoice_pdf, generate_report_pdf
import json
import os
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend which doesn't require a display
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64
from django.conf import settings
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField

# Helper functions for generating charts
def generate_pie_chart(labels, data, title, filename):
    """Generate a pie chart and save it to the staticfiles directory"""
    try:
        # Clear any previous plots
        plt.figure(figsize=(10, 6))
        plt.clf()

        # Create the pie chart
        plt.pie(data, labels=labels, autopct='%1.1f%%', startangle=90, 
                colors=['#f39c12', '#3498db', '#2ecc71', '#27ae60', '#e74c3c', '#9b59b6', '#34495e', '#1abc9c'])
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.title(title)

        # Ensure the charts directory exists
        charts_dir = os.path.join(settings.STATIC_ROOT, 'charts')
        os.makedirs(charts_dir, exist_ok=True)

        # Save the chart to the staticfiles directory
        chart_path = os.path.join(charts_dir, filename)
        plt.savefig(chart_path, bbox_inches='tight', dpi=100)
        plt.close()

        # Return the URL to the chart
        return os.path.join(settings.STATIC_URL, 'charts', filename)
    except Exception as e:
        print(f"Error generating pie chart '{title}': {str(e)}")
        # Return a fallback URL
        return f"{settings.STATIC_URL}admin/img/icon-no.svg"

def generate_bar_chart(labels, data, title, xlabel, ylabel, filename):
    """Generate a bar chart and save it to the staticfiles directory"""
    try:
        # Clear any previous plots
        plt.figure(figsize=(10, 6))
        plt.clf()

        # Create the bar chart
        x = np.arange(len(labels))
        plt.bar(x, data, color='#3498db')
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.xticks(x, labels, rotation=45, ha='right')
        plt.tight_layout()

        # Ensure the charts directory exists
        charts_dir = os.path.join(settings.STATIC_ROOT, 'charts')
        os.makedirs(charts_dir, exist_ok=True)

        # Save the chart to the staticfiles directory
        chart_path = os.path.join(charts_dir, filename)
        plt.savefig(chart_path, bbox_inches='tight', dpi=100)
        plt.close()

        # Return the URL to the chart
        return os.path.join(settings.STATIC_URL, 'charts', filename)
    except Exception as e:
        print(f"Error generating bar chart '{title}': {str(e)}")
        # Return a fallback URL
        return f"{settings.STATIC_URL}admin/img/icon-no.svg"

def generate_multi_bar_chart(labels, datasets, title, xlabel, ylabel, filename):
    """Generate a multi-series bar chart and save it to the staticfiles directory"""
    try:
        # Clear any previous plots
        plt.figure(figsize=(10, 6))
        plt.clf()

        # Create the bar chart with multiple series
        x = np.arange(len(labels))
        width = 0.35  # the width of the bars

        for i, dataset in enumerate(datasets):
            offset = width * (i - len(datasets)/2 + 0.5)
            plt.bar(x + offset, dataset['data'], width, label=dataset['label'], color=dataset.get('color', None))

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.xticks(x, labels, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()

        # Ensure the charts directory exists
        charts_dir = os.path.join(settings.STATIC_ROOT, 'charts')
        os.makedirs(charts_dir, exist_ok=True)

        # Save the chart to the staticfiles directory
        chart_path = os.path.join(charts_dir, filename)
        plt.savefig(chart_path, bbox_inches='tight', dpi=100)
        plt.close()

        # Return the URL to the chart
        return os.path.join(settings.STATIC_URL, 'charts', filename)
    except Exception as e:
        print(f"Error generating multi-bar chart '{title}': {str(e)}")
        # Return a fallback URL
        return f"{settings.STATIC_URL}admin/img/icon-no.svg"

@login_required
def home(request):
    """
    Ana sayfa görünümü - Dashboard

    Bu görünüm, sipariş durumları, ödeme durumları, stok seviyeleri ve
    diğer önemli istatistikleri içeren bir dashboard sunar.
    """
    try:
        # Sipariş durumlarına göre özet - tek sorguda tüm durumları al
        durumlar = ['beklemede', 'uretimde', 'tamamlandi', 'teslim_edildi', 'iptal_edildi']
        durum_labels = ['Beklemede', 'Üretimde', 'Tamamlandı', 'Teslim Edildi', 'İptal Edildi']

        # Veritabanından sipariş durumlarını al
        durum_rapor = Siparis.objects.values('durum').annotate(toplam=Count('id'))

        # Tüm durumları içeren bir özet hazırla (eksikleri 0 yap)
        siparis_ozet = {durum: 0 for durum in durumlar}
        siparis_ozet.update({item['durum']: item['toplam'] for item in durum_rapor})

        # Sipariş durumu grafiği için veri hazırla
        siparis_data = [siparis_ozet[durum] for durum in durumlar]

        # Sipariş durumu grafiği oluştur
        siparis_chart_url = generate_pie_chart(
            durum_labels, 
            siparis_data, 
            'Sipariş Durumu Dağılımı', 
            'siparis_durum_pie.png'
        )

        # Ödeme durumlarına göre özet - tek sorguda tüm ödeme durumlarını al
        odeme_durumlari = ['odenmedi', 'kismi_odendi', 'odendi']
        odeme_labels = ['Ödenmedi', 'Kısmen Ödendi', 'Ödendi']

        # Veritabanından ödeme durumlarını al
        odeme_rapor = Siparis.objects.values('odeme_durumu').annotate(
            toplam=Count('id'), 
            toplam_tutar=Sum('toplam_fiyat')
        )

        # Tüm ödeme durumlarını içeren bir özet hazırla (eksikleri 0 yap)
        odeme_ozet = {durum: {'adet': 0, 'tutar': 0} for durum in odeme_durumlari}
        for item in odeme_rapor:
            if item['odeme_durumu'] in odeme_ozet:
                odeme_ozet[item['odeme_durumu']] = {
                    'adet': item['toplam'],
                    'tutar': item['toplam_tutar'] or 0
                }

        # Ödeme durumu grafiği için veri hazırla
        odeme_adet_data = [odeme_ozet[durum]['adet'] for durum in odeme_durumlari]
        odeme_tutar_data = [float(odeme_ozet[durum]['tutar']) for durum in odeme_durumlari]

        # Ödeme durumu grafiği için veri setleri oluştur
        odeme_datasets = [
            {
                'label': 'Sipariş Sayısı',
                'data': odeme_adet_data,
                'color': '#3498db'
            },
            {
                'label': 'Tutar (TL)',
                'data': odeme_tutar_data,
                'color': '#2ecc71'
            }
        ]

        # Ödeme durumu grafiği oluştur
        odeme_chart_url = generate_multi_bar_chart(
            odeme_labels,
            odeme_datasets,
            'Ödeme Durumu Analizi',
            'Ödeme Durumu',
            'Değer',
            'odeme_durum_bar.png'
        )

        # Son 5 sipariş - ilişkili müşteri verilerini de getir (N+1 sorunu önleme)
        son_siparisler = Siparis.objects.select_related('musteri').order_by('-tarih', '-oncelik')[:5]

        # Son 5 ödeme - ilişkili sipariş ve müşteri verilerini de getir
        son_odemeler = Odeme.objects.select_related('siparis', 'siparis__musteri').order_by('-tarih')[:5]

        # Kritik stok seviyesindeki malzemeler
        kritik_stok = Malzeme.objects.filter(
            stok_miktari__gt=0,
            stok_miktari__lte=F('minimum_stok')  # Minimum stok seviyesinin altında olanlar
        ).order_by('stok_miktari')[:5]

        # Kritik stok grafiği için veri hazırla
        kritik_stok_labels = [m.ad for m in kritik_stok]
        kritik_stok_data = [m.stok_miktari for m in kritik_stok]

        # Kritik stok grafiği oluştur
        kritik_stok_chart_url = generate_bar_chart(
            kritik_stok_labels,
            kritik_stok_data,
            'Kritik Stok Seviyeleri',
            'Malzeme',
            'Stok Miktarı',
            'kritik_stok_bar.png'
        )

        # Malzeme türlerine göre stok dağılımı - veritabanı sorgusu ile optimize et
        from django.db.models import Case, When, CharField

        tur_rapor = Malzeme.objects.values(
            tur_adi=Case(
                *[When(tur=k, then=v) for k, v in dict(Malzeme.MALZEME_TURU_SECENEKLERI).items()],
                output_field=CharField()
            )
        ).annotate(toplam=Sum('stok_miktari')).order_by('tur_adi')

        # Malzeme türleri grafiği için veri hazırla
        tur_labels = [item['tur_adi'] for item in tur_rapor]
        tur_data = [item['toplam'] for item in tur_rapor]

        # Malzeme türleri grafiği oluştur
        tur_chart_url = generate_pie_chart(
            tur_labels,
            tur_data,
            'Malzeme Türlerine Göre Stok Dağılımı',
            'malzeme_tur_pie.png'
        )

        # Toplam istatistikler - tek sorguda hesapla
        from django.db.models import Q, F, ExpressionWrapper, DecimalField

        # Sipariş sayıları
        siparis_sayilari = {
            'toplam_siparis': Siparis.objects.count(),
            'bekleyen_siparis': Siparis.objects.filter(durum__in=['beklemede', 'uretimde']).count(),
            'tamamlanan_siparis': Siparis.objects.filter(durum='tamamlandi').count(),
        }

        # Finansal istatistikler
        finansal_ozet = Siparis.objects.aggregate(
            toplam_ciro=Sum('toplam_fiyat'),
            tahsil_edilen=Sum('odenen_miktar'),
            bekleyen_tahsilat=ExpressionWrapper(
                Sum('toplam_fiyat') - Sum('odenen_miktar'),
                output_field=DecimalField()
            )
        )

        # None değerleri 0'a çevir
        for key, value in finansal_ozet.items():
            if value is None:
                finansal_ozet[key] = 0

        # Tüm istatistikleri birleştir
        toplam_istatistikler = {**siparis_sayilari, **finansal_ozet}

        # Öncelikli siparişler
        oncelikli_siparisler = Siparis.objects.filter(
            Q(durum__in=['beklemede', 'uretimde']) & Q(oncelik__gt=0)
        ).select_related('musteri').order_by('-oncelik', 'tarih')[:3]

        # Gecikmiş siparişler (teslim tarihi geçmiş ama tamamlanmamış)
        from django.utils import timezone

        gecikmiş_siparisler = Siparis.objects.filter(
            Q(durum__in=['beklemede', 'uretimde']) & 
            Q(teslim_tarihi__lt=timezone.now().date()) &
            ~Q(teslim_tarihi=None)
        ).select_related('musteri').order_by('teslim_tarihi')[:3]

        return render(request, 'home.html', {
            'siparis_ozet': siparis_ozet,
            'odeme_ozet': odeme_ozet,
            'son_siparisler': son_siparisler,
            'son_odemeler': son_odemeler,
            'kritik_stok': kritik_stok,
            'toplam_istatistikler': toplam_istatistikler,
            'siparis_chart_url': siparis_chart_url,
            'odeme_chart_url': odeme_chart_url,
            'kritik_stok_chart_url': kritik_stok_chart_url,
            'tur_chart_url': tur_chart_url,
            'oncelikli_siparisler': oncelikli_siparisler,
            'gecikmiş_siparisler': gecikmiş_siparisler,
        })

    except Exception as e:
        # Hata durumunda log oluştur ve basit bir hata sayfası göster
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Dashboard görüntülenirken hata oluştu: {str(e)}")

        messages.error(request, "Dashboard yüklenirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.")
        return render(request, 'error.html', {
            'error_message': "Dashboard yüklenirken bir hata oluştu.",
            'error_details': str(e) if settings.DEBUG else None
        })

def musteri_ekle(request):
    if request.method == "POST":
        isim = request.POST.get("isim")
        telefon = request.POST.get("telefon")
        adres = request.POST.get("adres")
        firmasi = request.POST.get("firmasi")

        if isim:
            Musteri.objects.create(isim=isim, telefon=telefon, adres=adres, firmasi=firmasi)
            messages.success(request, "Müşteri başarıyla eklendi.")
            return redirect("musteriler_listesi")
        else:
            messages.error(request, "İsim alanı zorunludur!")

    return render(request, "musteri_ekle.html")


@login_required
def siparisler_listesi(request):
    """
    Siparişleri listeleyen görünüm.

    Bu görünüm, çeşitli filtreleme ve sıralama seçenekleriyle siparişleri listeler.
    Arama, durum, müşteri, tarih aralığı ve sıralama kriterleri desteklenir.
    """
    try:
        # Filtre parametrelerini al
        arama = request.GET.get('arama', '').strip()
        durum = request.GET.get('durum')
        musteri_id = request.GET.get('musteri')
        baslangic = request.GET.get('baslangic_tarih')
        bitis = request.GET.get('bitis_tarih')
        sirala = request.GET.get('sirala', '-tarih')
        odeme_durumu = request.GET.get('odeme_durumu')
        oncelik = request.GET.get('oncelik')

        # Sayfalama için sayfa numarasını al
        sayfa = request.GET.get('sayfa', 1)
        sayfa_boyutu = 25  # Her sayfada gösterilecek sipariş sayısı

        # Temel sorgu - ilişkili müşteri verilerini de getir (N+1 sorunu önleme)
        siparisler = Siparis.objects.select_related('musteri').all()

        # Filtreleri uygula
        if durum:
            siparisler = siparisler.filter(durum=durum)

        if musteri_id:
            siparisler = siparisler.filter(musteri_id=musteri_id)

        if odeme_durumu:
            siparisler = siparisler.filter(odeme_durumu=odeme_durumu)

        if oncelik:
            siparisler = siparisler.filter(oncelik=oncelik)

        # Tarih filtrelerini uygula
        if baslangic:
            try:
                siparisler = siparisler.filter(tarih__gte=baslangic)
            except ValueError:
                messages.warning(request, "Geçersiz başlangıç tarihi formatı. Tarih filtresi uygulanmadı.")

        if bitis:
            try:
                siparisler = siparisler.filter(tarih__lte=bitis)
            except ValueError:
                messages.warning(request, "Geçersiz bitiş tarihi formatı. Tarih filtresi uygulanmadı.")

        # Arama filtresini uygula - Q nesneleri ile daha verimli arama
        if arama:
            from django.db.models import Q
            siparisler = siparisler.filter(
                Q(urun_tipi__icontains=arama) |
                Q(musteri__isim__icontains=arama) |
                Q(musteri__firmasi__icontains=arama) |
                Q(aciklama__icontains=arama)
            )

        # Toplam sipariş sayısını kaydet
        toplam_siparis_sayisi = siparisler.count()

        # Sıralama uygula
        try:
            siparisler = siparisler.order_by(sirala)
        except Exception:
            messages.warning(request, "Geçersiz sıralama kriteri. Varsayılan sıralama uygulandı.")
            siparisler = siparisler.order_by('-tarih')
            sirala = '-tarih'

        # Sayfalama uygula
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

        paginator = Paginator(siparisler, sayfa_boyutu)

        try:
            sayfalanmis_siparisler = paginator.page(sayfa)
        except PageNotAnInteger:
            # Sayfa numarası bir tamsayı değilse, ilk sayfayı göster
            sayfalanmis_siparisler = paginator.page(1)
        except EmptyPage:
            # Sayfa numarası aralık dışındaysa, son sayfayı göster
            sayfalanmis_siparisler = paginator.page(paginator.num_pages)

        # Dropdown menüler için verileri hazırla
        musteriler = Musteri.objects.all().order_by('isim')

        # Durum ve ödeme durumu seçenekleri
        durum_secenekleri = Siparis.DURUM_SECENEKLERI
        odeme_durumu_secenekleri = Siparis.ODEME_DURUMU_SECENEKLERI
        oncelik_secenekleri = Siparis.ONCELIK_SECENEKLERI

        # Özet istatistikler
        from django.db.models import Count, Sum

        ozet_istatistikler = {
            'toplam_siparis': toplam_siparis_sayisi,
            'toplam_tutar': siparisler.aggregate(toplam=Sum('toplam_fiyat'))['toplam'] or 0,
            'odenen_tutar': siparisler.aggregate(toplam=Sum('odenen_miktar'))['toplam'] or 0,
        }

        # Durumlara göre dağılım
        durum_dagilimi = siparisler.values('durum').annotate(toplam=Count('id'))
        durum_ozeti = {item['durum']: item['toplam'] for item in durum_dagilimi}

        return render(request, "siparisler_listesi.html", {
            "siparisler": sayfalanmis_siparisler,
            "musteriler": musteriler,
            "durum_secenekleri": durum_secenekleri,
            "odeme_durumu_secenekleri": odeme_durumu_secenekleri,
            "oncelik_secenekleri": oncelik_secenekleri,
            "aktif_musteri": musteri_id,
            "aktif_durum": durum,
            "aktif_odeme_durumu": odeme_durumu,
            "aktif_oncelik": oncelik,
            "aktif_arama": arama,
            "baslangic": baslangic,
            "bitis": bitis,
            "sirala": sirala,
            "ozet_istatistikler": ozet_istatistikler,
            "durum_ozeti": durum_ozeti,
            "toplam_siparis_sayisi": toplam_siparis_sayisi,
        })

    except Exception as e:
        # Hata durumunda log oluştur ve hata mesajı göster
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Siparişler listelenirken hata oluştu: {str(e)}")

        messages.error(request, "Siparişler listelenirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.")

        # Boş bir sipariş listesi ile sayfayı göster
        return render(request, "siparisler_listesi.html", {
            "siparisler": [],
            "musteriler": Musteri.objects.all().order_by('isim'),
            "durum_secenekleri": Siparis.DURUM_SECENEKLERI,
            "error_message": "Siparişler listelenirken bir hata oluştu.",
            "error_details": str(e) if settings.DEBUG else None
        })
def siparis_ekle(request):
    musteriler = Musteri.objects.all()
    if request.method == "POST":
        musteri_id = request.POST.get("musteri")
        urun_tipi = request.POST.get("urun_tipi")
        iscilik_turu = request.POST.get("iscilik_turu")
        aciklama = request.POST.get("aciklama")

        # Get additional fields
        try:
            adet = int(request.POST.get("adet", 1))
            birim_fiyat = Decimal(request.POST.get("birim_fiyat", 0))
            oncelik = int(request.POST.get("oncelik", 0))
        except (ValueError, TypeError):
            messages.error(request, "Geçersiz sayısal değer. Lütfen sayısal alanları doğru formatta doldurun.")
            return render(request, "siparis_ekle.html", {"musteriler": musteriler})

        musteri = Musteri.objects.get(id=musteri_id)
        Siparis.objects.create(
            musteri=musteri,
            urun_tipi=urun_tipi,
            adet=adet,
            iscilik_turu=iscilik_turu,
            aciklama=aciklama,
            birim_fiyat=birim_fiyat,
            oncelik=oncelik
        )
        messages.success(request, "Sipariş başarıyla oluşturuldu.")
        return redirect("siparisler_listesi")
    return render(request, "siparis_ekle.html", {"musteriler": musteriler})


def siparis_detay(request, siparis_id):
    siparis = get_object_or_404(Siparis, id=siparis_id)
    if request.method == "POST":
        yeni_durum = request.POST.get("durum")
        if yeni_durum in dict(Siparis.DURUM_SECENEKLERI):
            siparis.durum = yeni_durum
            siparis.save()
            messages.success(request, f"Sipariş durumu '{siparis.get_durum_display()}' olarak güncellendi.")
        return redirect("siparis_detay", siparis_id=siparis.id)
    return render(request, "siparis_detay.html", {"siparis": siparis})

@login_required
def odeme_ekle(request, siparis_id):
    siparis = get_object_or_404(Siparis, id=siparis_id)

    if request.method == "POST":
        try:
            miktar = Decimal(request.POST.get("miktar", "0"))
            aciklama = request.POST.get("aciklama", "")

            if miktar <= 0:
                messages.error(request, "Ödeme miktarı sıfırdan büyük olmalıdır.")
                return redirect("odeme_ekle", siparis_id=siparis.id)

            if miktar > siparis.kalan_odeme():
                messages.error(request, f"Ödeme miktarı kalan ödemeden ({siparis.kalan_odeme()} TL) fazla olamaz.")
                return redirect("odeme_ekle", siparis_id=siparis.id)

            # Ödeme ekle
            odeme = siparis.odeme_yap(miktar, aciklama)

            messages.success(request, f"{miktar} TL tutarında ödeme başarıyla kaydedildi.")
            return redirect("siparis_detay", siparis_id=siparis.id)

        except ValueError:
            messages.error(request, "Geçersiz ödeme miktarı.")
            return redirect("odeme_ekle", siparis_id=siparis.id)

    return render(request, "odeme_ekle.html", {"siparis": siparis})

@login_required
def malzeme_ekle(request, siparis_id):
    siparis = get_object_or_404(Siparis, id=siparis_id)
    malzemeler = Malzeme.objects.filter(stok_miktari__gt=0).order_by('ad')

    if request.method == "POST":
        try:
            malzeme_id = request.POST.get("malzeme_id")
            miktar = int(request.POST.get("miktar", "0"))

            if not malzeme_id:
                messages.error(request, "Lütfen bir malzeme seçin.")
                return redirect("malzeme_ekle", siparis_id=siparis.id)

            if miktar <= 0:
                messages.error(request, "Miktar sıfırdan büyük olmalıdır.")
                return redirect("malzeme_ekle", siparis_id=siparis.id)

            malzeme = get_object_or_404(Malzeme, id=malzeme_id)

            if miktar > malzeme.stok_miktari:
                messages.error(request, f"Yetersiz stok: {malzeme.stok_miktari} {malzeme.birim} mevcut, {miktar} {malzeme.birim} talep edildi.")
                return redirect("malzeme_ekle", siparis_id=siparis.id)

            # Malzeme kullanımı ekle
            kullanim = MalzemeKullanimi.objects.create(
                siparis=siparis,
                malzeme=malzeme,
                miktar=miktar
            )

            messages.success(request, f"{miktar} {malzeme.birim} {malzeme.ad} siparişe eklendi.")
            return redirect("siparis_detay", siparis_id=siparis.id)

        except ValueError:
            messages.error(request, "Geçersiz miktar.")
            return redirect("malzeme_ekle", siparis_id=siparis.id)

    return render(request, "malzeme_ekle.html", {
        "siparis": siparis,
        "malzemeler": malzemeler
    })

def musteri_duzenle(request, musteri_id):
    musteri = get_object_or_404(Musteri, id=musteri_id)
    if request.method == "POST":
        musteri.isim = request.POST.get("isim")
        musteri.firmasi = request.POST.get("firmasi")
        musteri.telefon = request.POST.get("telefon")
        musteri.adres = request.POST.get("adres")
        musteri.save()
        return redirect("musteriler_listesi")
    return render(request, "musteri_duzenle.html", {"musteri": musteri})

def musteri_sil(request, musteri_id):
    musteri = get_object_or_404(Musteri, id=musteri_id)
    if request.method == "POST":
        musteri.delete()
        return redirect("musteriler_listesi")
    return render(request, "musteri_sil_onay.html", {"musteri": musteri})
def siparis_duzenle(request, siparis_id):
    siparis = get_object_or_404(Siparis, id=siparis_id)
    musteriler = Musteri.objects.all()
    if request.method == "POST":
        musteri_id = request.POST.get("musteri")
        siparis.musteri = Musteri.objects.get(id=musteri_id)
        siparis.urun_tipi = request.POST.get("urun_tipi")
        siparis.iscilik_turu = request.POST.get("iscilik_turu")
        siparis.durum = request.POST.get("durum")
        siparis.aciklama = request.POST.get("aciklama")
        siparis.save()
        return redirect("siparisler_listesi")
    return render(request, "siparis_duzenle.html", {"siparis": siparis, "musteriler": musteriler})

def siparis_sil(request, siparis_id):
    siparis = get_object_or_404(Siparis, id=siparis_id)
    if request.method == "POST":
        siparis.delete()
        return redirect("siparisler_listesi")
    return render(request, "siparis_sil_onay.html", {"siparis": siparis})


def musteriler_listesi(request):
    arama = request.GET.get('arama')
    musteriler = Musteri.objects.all()
    if arama:
        musteriler = musteriler.filter(isim__icontains=arama) | musteriler.filter(firmasi__icontains=arama)
    return render(request, "musteriler_listesi.html", {"musteriler": musteriler, "aktif_arama": arama})

@login_required
def malzemeler_listesi(request):
    arama = request.GET.get('arama')
    tur = request.GET.get('tur')
    sirala = request.GET.get('sirala', 'ad')

    malzemeler = Malzeme.objects.all()

    if tur:
        malzemeler = malzemeler.filter(tur=tur)
    if arama:
        malzemeler = malzemeler.filter(ad__icontains=arama) | malzemeler.filter(aciklama__icontains=arama)

    malzemeler = malzemeler.order_by(sirala)

    # Malzeme türlerine göre stok miktarlarını topla
    tur_toplam_stok = {}
    for malzeme in Malzeme.objects.all():
        tur_adi = malzeme.get_tur_display()
        if tur_adi not in tur_toplam_stok:
            tur_toplam_stok[tur_adi] = 0
        tur_toplam_stok[tur_adi] += malzeme.stok_miktari

    # Malzeme türleri grafiği oluştur
    tur_labels = list(tur_toplam_stok.keys())
    tur_data = list(tur_toplam_stok.values())

    tur_chart_url = generate_pie_chart(
        tur_labels,
        tur_data,
        'Malzeme Türlerine Göre Stok Dağılımı',
        'malzeme_tur_pie_list.png'
    )

    # En çok stoğu olan 10 malzemeyi bul
    top_malzemeler = Malzeme.objects.order_by('-stok_miktari')[:10]

    # Top malzemeler grafiği oluştur
    top_malzeme_labels = [m.ad for m in top_malzemeler]
    top_malzeme_data = [m.stok_miktari for m in top_malzemeler]

    top_malzeme_chart_url = generate_bar_chart(
        top_malzeme_labels,
        top_malzeme_data,
        'En Çok Stoğu Olan 10 Malzeme',
        'Malzeme',
        'Stok Miktarı',
        'top_malzeme_bar.png'
    )

    return render(request, "malzemeler_listesi.html", {
        "malzemeler": malzemeler,
        "aktif_tur": tur,
        "aktif_arama": arama,
        "sirala": sirala,
        "tur_secenekleri": Malzeme.MALZEME_TURU_SECENEKLERI,
        "tur_chart_url": tur_chart_url,
        "top_malzeme_chart_url": top_malzeme_chart_url
    })

@login_required
def malzeme_detay(request, malzeme_id):
    malzeme = get_object_or_404(Malzeme, id=malzeme_id)
    kullanim_kayitlari = MalzemeKullanimi.objects.filter(malzeme=malzeme).select_related('siparis', 'siparis__musteri').order_by('-tarih')

    return render(request, "malzeme_detay.html", {
        "malzeme": malzeme,
        "kullanim_kayitlari": kullanim_kayitlari
    })

@login_required
def malzeme_duzenle(request, malzeme_id=None):
    if malzeme_id:
        malzeme = get_object_or_404(Malzeme, id=malzeme_id)
        baslik = "Malzeme Düzenle"
    else:
        malzeme = None
        baslik = "Yeni Malzeme Ekle"

    if request.method == "POST":
        ad = request.POST.get("ad")
        tur = request.POST.get("tur")
        stok_miktari = int(request.POST.get("stok_miktari", 0))
        birim = request.POST.get("birim")
        birim_fiyat = Decimal(request.POST.get("birim_fiyat", 0))
        aciklama = request.POST.get("aciklama", "")

        if not ad:
            messages.error(request, "Malzeme adı zorunludur!")
            return redirect("malzeme_duzenle", malzeme_id=malzeme_id) if malzeme_id else redirect("malzeme_ekle")

        if malzeme:
            # Mevcut malzemeyi güncelle
            malzeme.ad = ad
            malzeme.tur = tur
            malzeme.stok_miktari = stok_miktari
            malzeme.birim = birim
            malzeme.birim_fiyat = birim_fiyat
            malzeme.aciklama = aciklama
            malzeme.save()
            messages.success(request, "Malzeme başarıyla güncellendi.")
        else:
            # Yeni malzeme oluştur
            malzeme = Malzeme.objects.create(
                ad=ad,
                tur=tur,
                stok_miktari=stok_miktari,
                birim=birim,
                birim_fiyat=birim_fiyat,
                aciklama=aciklama
            )
            messages.success(request, "Malzeme başarıyla eklendi.")

        return redirect("malzemeler_listesi")

    return render(request, "malzeme_form.html", {
        "malzeme": malzeme,
        "baslik": baslik,
        "tur_secenekleri": Malzeme.MALZEME_TURU_SECENEKLERI
    })

@login_required
def malzeme_sil(request, malzeme_id):
    malzeme = get_object_or_404(Malzeme, id=malzeme_id)

    if request.method == "POST":
        try:
            malzeme.delete()
            messages.success(request, "Malzeme başarıyla silindi.")
            return redirect("malzemeler_listesi")
        except models.ProtectedError:
            messages.error(request, "Bu malzeme siparişlerde kullanıldığı için silinemez.")

    return render(request, "malzeme_sil_onay.html", {"malzeme": malzeme})

@login_required
def malzeme_kullanimi_listesi(request):
    arama = request.GET.get('arama')
    malzeme_id = request.GET.get('malzeme')
    siparis_id = request.GET.get('siparis')
    baslangic = request.GET.get('baslangic_tarih')
    bitis = request.GET.get('bitis_tarih')
    sirala = request.GET.get('sirala', '-tarih')

    kullanim_kayitlari = MalzemeKullanimi.objects.select_related('malzeme', 'siparis', 'siparis__musteri').all()

    if malzeme_id:
        kullanim_kayitlari = kullanim_kayitlari.filter(malzeme_id=malzeme_id)
    if siparis_id:
        kullanim_kayitlari = kullanim_kayitlari.filter(siparis_id=siparis_id)
    if baslangic:
        kullanim_kayitlari = kullanim_kayitlari.filter(tarih__date__gte=baslangic)
    if bitis:
        kullanim_kayitlari = kullanim_kayitlari.filter(tarih__date__lte=bitis)
    if arama:
        kullanim_kayitlari = kullanim_kayitlari.filter(
            malzeme__ad__icontains=arama
        ) | kullanim_kayitlari.filter(
            siparis__urun_tipi__icontains=arama
        ) | kullanim_kayitlari.filter(
            siparis__musteri__isim__icontains=arama
        )

    kullanim_kayitlari = kullanim_kayitlari.order_by(sirala)

    malzemeler = Malzeme.objects.all()
    siparisler = Siparis.objects.select_related('musteri').all()

    return render(request, "malzeme_kullanimi_listesi.html", {
        "kullanim_kayitlari": kullanim_kayitlari,
        "malzemeler": malzemeler,
        "siparisler": siparisler,
        "aktif_malzeme": malzeme_id,
        "aktif_siparis": siparis_id,
        "aktif_arama": arama,
        "baslangic": baslangic,
        "bitis": bitis,
        "sirala": sirala
    })

@login_required
def raporlar_listesi(request):
    arama = request.GET.get('arama')
    tip = request.GET.get('tip')
    sirala = request.GET.get('sirala', '-olusturulma_tarihi')

    raporlar = Rapor.objects.all()

    if tip:
        raporlar = raporlar.filter(tip=tip)
    if arama:
        raporlar = raporlar.filter(baslik__icontains=arama)

    raporlar = raporlar.order_by(sirala)

    return render(request, "raporlar_listesi.html", {
        "raporlar": raporlar,
        "aktif_tip": tip,
        "aktif_arama": arama,
        "sirala": sirala,
        "tip_secenekleri": Rapor.RAPOR_TIPLERI
    })

@login_required
def rapor_olustur(request):
    if request.method == "POST":
        baslik = request.POST.get("baslik")
        tip = request.POST.get("tip")
        baslangic_tarihi = request.POST.get("baslangic_tarihi")
        bitis_tarihi = request.POST.get("bitis_tarihi")

        if not all([baslik, tip, baslangic_tarihi, bitis_tarihi]):
            messages.error(request, "Tüm alanlar zorunludur!")
            return redirect("rapor_olustur")

        # Tarih aralığındaki siparişleri bul
        siparisler = Siparis.objects.filter(
            tarih__gte=baslangic_tarihi,
            tarih__lte=bitis_tarihi
        )

        # Rapor istatistiklerini hesapla
        toplam_siparis = siparisler.count()
        toplam_gelir = siparisler.aggregate(toplam=Sum('toplam_fiyat'))['toplam'] or 0

        # Raporu oluştur
        rapor = Rapor.objects.create(
            baslik=baslik,
            tip=tip,
            baslangic_tarihi=baslangic_tarihi,
            bitis_tarihi=bitis_tarihi,
            toplam_siparis=toplam_siparis,
            toplam_gelir=toplam_gelir
        )

        messages.success(request, "Rapor başarıyla oluşturuldu.")
        return redirect("raporlar_listesi")

    return render(request, "rapor_olustur.html", {
        "tip_secenekleri": Rapor.RAPOR_TIPLERI
    })

@login_required
def rapor_detay(request, rapor_id):
    rapor = get_object_or_404(Rapor, id=rapor_id)

    # Rapor tarih aralığındaki siparişleri bul
    siparisler = Siparis.objects.filter(
        tarih__gte=rapor.baslangic_tarihi,
        tarih__lte=rapor.bitis_tarihi
    ).select_related('musteri')

    # Durumlara göre sipariş sayıları
    durum_ozeti = siparisler.values('durum').annotate(toplam=Count('id'))
    durum_istatistikleri = {item['durum']: item['toplam'] for item in durum_ozeti}

    # Sipariş durumu grafiği için veri hazırla
    durumlar = ['beklemede', 'uretimde', 'tamamlandi', 'teslim_edildi', 'iptal_edildi']
    durum_labels = ['Beklemede', 'Üretimde', 'Tamamlandı', 'Teslim Edildi', 'İptal Edildi']
    durum_data = [durum_istatistikleri.get(durum, 0) for durum in durumlar]

    # Sipariş durumu grafiği oluştur
    durum_chart_url = generate_pie_chart(
        durum_labels, 
        durum_data, 
        'Sipariş Durumu Dağılımı', 
        f'rapor_{rapor_id}_durum_pie.png'
    )

    # Müşterilere göre sipariş sayıları
    musteri_ozeti = siparisler.values('musteri__isim').annotate(
        toplam=Count('id'),
        toplam_tutar=Sum('toplam_fiyat')
    ).order_by('-toplam')[:10]

    # Müşteri grafiği için veri hazırla
    musteri_labels = [item['musteri__isim'] for item in musteri_ozeti]
    musteri_data = [item['toplam'] for item in musteri_ozeti]

    # Müşteri grafiği oluştur
    musteri_chart_url = generate_bar_chart(
        musteri_labels,
        musteri_data,
        'En Çok Sipariş Veren Müşteriler',
        'Müşteri',
        'Sipariş Sayısı',
        f'rapor_{rapor_id}_musteri_bar.png'
    )

    # İşçilik türlerine göre sipariş sayıları
    iscilik_ozeti = siparisler.values('iscilik_turu').annotate(toplam=Count('id'))
    iscilik_istatistikleri = {item['iscilik_turu']: item['toplam'] for item in iscilik_ozeti}

    # İşçilik türü grafiği için veri hazırla
    iscilik_turleri = ['taslama', 'krom_kaplama', 'honlama', 'polisaj', 'diger']
    iscilik_labels = ['Taşlama', 'Krom Kaplama', 'Honlama', 'Polisaj', 'Diğer']
    iscilik_data = [iscilik_istatistikleri.get(tur, 0) for tur in iscilik_turleri]

    # İşçilik türü grafiği oluştur
    iscilik_chart_url = generate_pie_chart(
        iscilik_labels,
        iscilik_data,
        'İşçilik Türü Dağılımı',
        f'rapor_{rapor_id}_iscilik_pie.png'
    )

    # Günlük gelir grafiği için veri hazırla
    from django.db.models.functions import TruncDate

    # Günlük gelir verilerini al
    gunluk_gelir = siparisler.annotate(
        gun=TruncDate('tarih')
    ).values('gun').annotate(
        toplam=Sum('toplam_fiyat')
    ).order_by('gun')

    # Gün ve gelir miktarları
    gunler = [item['gun'].strftime('%d.%m.%Y') for item in gunluk_gelir]
    gelirler = [float(item['toplam']) for item in gunluk_gelir]

    # Günlük gelir grafiği oluştur
    gelir_chart_url = generate_bar_chart(
        gunler,
        gelirler,
        'Günlük Gelir Dağılımı',
        'Tarih',
        'Gelir (TL)',
        f'rapor_{rapor_id}_gelir_bar.png'
    )

    return render(request, "rapor_detay.html", {
        "rapor": rapor,
        "siparisler": siparisler,
        "durum_istatistikleri": durum_istatistikleri,
        "musteri_ozeti": musteri_ozeti,
        "iscilik_istatistikleri": iscilik_istatistikleri,
        "durum_chart_url": durum_chart_url,
        "musteri_chart_url": musteri_chart_url,
        "iscilik_chart_url": iscilik_chart_url,
        "gelir_chart_url": gelir_chart_url
    })

@login_required
def rapor_sil(request, rapor_id):
    rapor = get_object_or_404(Rapor, id=rapor_id)

    if request.method == "POST":
        rapor.delete()
        messages.success(request, "Rapor başarıyla silindi.")
        return redirect("raporlar_listesi")

    return render(request, "rapor_sil_onay.html", {"rapor": rapor})

@login_required
def odemeler_listesi(request):
    arama = request.GET.get('arama')
    siparis_id = request.GET.get('siparis')
    musteri_id = request.GET.get('musteri')
    baslangic = request.GET.get('baslangic_tarih')
    bitis = request.GET.get('bitis_tarih')
    sirala = request.GET.get('sirala', '-tarih')

    odemeler = Odeme.objects.select_related('siparis', 'siparis__musteri').all()

    if siparis_id:
        odemeler = odemeler.filter(siparis_id=siparis_id)
    if musteri_id:
        odemeler = odemeler.filter(siparis__musteri_id=musteri_id)
    if baslangic:
        odemeler = odemeler.filter(tarih__date__gte=baslangic)
    if bitis:
        odemeler = odemeler.filter(tarih__date__lte=bitis)
    if arama:
        odemeler = odemeler.filter(
            siparis__urun_tipi__icontains=arama
        ) | odemeler.filter(
            siparis__musteri__isim__icontains=arama
        ) | odemeler.filter(
            aciklama__icontains=arama
        )

    odemeler = odemeler.order_by(sirala)

    # Aylık ödeme analizi için veri hazırla
    from django.db.models.functions import TruncMonth

    # Son 6 ay için ödeme verilerini al
    from datetime import datetime, timedelta
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=180)  # Son 6 ay

    monthly_payments = Odeme.objects.filter(
        tarih__date__gte=start_date,
        tarih__date__lte=end_date
    ).annotate(
        month=TruncMonth('tarih')
    ).values('month').annotate(
        total=Sum('miktar')
    ).order_by('month')

    # Ay isimleri ve ödeme miktarları
    months = []
    amounts = []

    # Türkçe ay isimleri
    month_names = {
        1: 'Ocak', 2: 'Şubat', 3: 'Mart', 4: 'Nisan', 5: 'Mayıs', 6: 'Haziran',
        7: 'Temmuz', 8: 'Ağustos', 9: 'Eylül', 10: 'Ekim', 11: 'Kasım', 12: 'Aralık'
    }

    for payment in monthly_payments:
        month_name = month_names[payment['month'].month]
        months.append(f"{month_name} {payment['month'].year}")
        amounts.append(float(payment['total']))

    # Veri yoksa örnek veri kullan
    if not months:
        months = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran']
        amounts = [12000, 19000, 15000, 25000, 22000, 30000]

    # Ödeme grafiği oluştur
    odeme_chart_url = generate_bar_chart(
        months,
        amounts,
        'Aylık Ödeme Analizi',
        'Ay',
        'Miktar (TL)',
        'aylik_odeme_bar.png'
    )

    siparisler = Siparis.objects.select_related('musteri').all()
    musteriler = Musteri.objects.all()

    return render(request, "odemeler_listesi.html", {
        "odemeler": odemeler,
        "siparisler": siparisler,
        "musteriler": musteriler,
        "aktif_siparis": siparis_id,
        "aktif_musteri": musteri_id,
        "aktif_arama": arama,
        "baslangic": baslangic,
        "bitis": bitis,
        "sirala": sirala,
        "odeme_chart_url": odeme_chart_url
    })

@login_required
def grafik_sayfasi(request):
    """Grafik sayfası - Stok ve müşteri ödeme bilgilerini görselleştirir"""

    # 1. Stok Grafikleri

    # 1.1 Malzeme türlerine göre stok dağılımı
    tur_toplam_stok = {}
    for malzeme in Malzeme.objects.all():
        tur_adi = malzeme.get_tur_display()
        if tur_adi not in tur_toplam_stok:
            tur_toplam_stok[tur_adi] = 0
        tur_toplam_stok[tur_adi] += malzeme.stok_miktari

    # Malzeme türleri grafiği oluştur
    tur_labels = list(tur_toplam_stok.keys())
    tur_data = list(tur_toplam_stok.values())

    tur_chart_url = generate_pie_chart(
        tur_labels,
        tur_data,
        'Malzeme Türlerine Göre Stok Dağılımı',
        'malzeme_tur_pie_grafik.png'
    )

    # 1.2 En çok stoğu olan 10 malzeme
    top_malzemeler = Malzeme.objects.order_by('-stok_miktari')[:10]

    # Top malzemeler grafiği oluştur
    top_malzeme_labels = [m.ad for m in top_malzemeler]
    top_malzeme_data = [m.stok_miktari for m in top_malzemeler]

    top_malzeme_chart_url = generate_bar_chart(
        top_malzeme_labels,
        top_malzeme_data,
        'En Çok Stoğu Olan 10 Malzeme',
        'Malzeme',
        'Stok Miktarı',
        'top_malzeme_bar_grafik.png'
    )

    # 2. Müşteri Ödeme Grafikleri

    # 2.1 Müşterilere göre toplam borç ve ödeme durumu
    musteri_odemeler = Musteri.objects.annotate(
        toplam_borc=Sum('siparisler__toplam_fiyat'),
        odenen_miktar=Sum('siparisler__odenen_miktar'),
        kalan_borc=ExpressionWrapper(
            F('toplam_borc') - F('odenen_miktar'),
            output_field=DecimalField()
        )
    ).filter(toplam_borc__gt=0).order_by('-toplam_borc')[:10]

    # Müşteri ödeme grafiği oluştur
    musteri_labels = [m.isim for m in musteri_odemeler]

    musteri_datasets = [
        {
            'label': 'Toplam Borç',
            'data': [float(m.toplam_borc or 0) for m in musteri_odemeler],
            'color': '#e74c3c'  # Kırmızı
        },
        {
            'label': 'Ödenen Miktar',
            'data': [float(m.odenen_miktar or 0) for m in musteri_odemeler],
            'color': '#2ecc71'  # Yeşil
        }
    ]

    musteri_odeme_chart_url = generate_multi_bar_chart(
        musteri_labels,
        musteri_datasets,
        'Müşterilere Göre Borç ve Ödeme Durumu',
        'Müşteri',
        'Miktar (TL)',
        'musteri_odeme_bar_grafik.png'
    )

    # 2.2 Toplam ödeme durumu (ödenmiş vs ödenmemiş)
    toplam_borc = Siparis.objects.aggregate(toplam=Sum('toplam_fiyat'))['toplam'] or 0
    toplam_odenen = Siparis.objects.aggregate(toplam=Sum('odenen_miktar'))['toplam'] or 0
    toplam_kalan = toplam_borc - toplam_odenen

    odeme_durumu_labels = ['Ödenen', 'Kalan Borç']
    odeme_durumu_data = [float(toplam_odenen), float(toplam_kalan)]

    odeme_durumu_chart_url = generate_pie_chart(
        odeme_durumu_labels,
        odeme_durumu_data,
        'Toplam Ödeme Durumu',
        'odeme_durumu_pie_grafik.png'
    )

    return render(request, "grafik_sayfasi.html", {
        'tur_chart_url': tur_chart_url,
        'top_malzeme_chart_url': top_malzeme_chart_url,
        'musteri_odeme_chart_url': musteri_odeme_chart_url,
        'odeme_durumu_chart_url': odeme_durumu_chart_url,
        'toplam_borc': toplam_borc,
        'toplam_odenen': toplam_odenen,
        'toplam_kalan': toplam_kalan,
    })

@login_required
def siparis_pdf(request, siparis_id):
    """
    Sipariş için PDF fatura oluşturur ve indirir.
    """
    siparis = get_object_or_404(Siparis, id=siparis_id)
    return generate_invoice_pdf(siparis)

@login_required
def rapor_pdf(request, rapor_id):
    """
    Rapor için PDF dosyası oluşturur ve indirir.
    """
    rapor = get_object_or_404(Rapor, id=rapor_id)
    return generate_report_pdf(rapor)

def yardim(request):
    """
    Yardım sayfasını gösterir.
    """
    return render(request, "yardim.html")

def gizlilik_politikasi(request):
    """
    Gizlilik politikası sayfasını gösterir.
    """
    return render(request, "gizlilik_politikasi.html")

def iletisim(request):
    """
    İletişim sayfasını gösterir.
    """
    return render(request, "iletisim.html")
