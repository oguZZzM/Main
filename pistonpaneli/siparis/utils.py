from django.template.loader import render_to_string
from django.conf import settings
import os
import tempfile
from weasyprint import HTML, CSS
from django.http import HttpResponse
from datetime import datetime
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.utils.html import strip_tags

def generate_pdf(template_name, context, filename):
    """
    Generate a PDF file from a template and context.

    Args:
        template_name (str): The name of the template to render
        context (dict): The context to pass to the template
        filename (str): The filename for the PDF

    Returns:
        HttpResponse: A response with the PDF file
    """
    # Add some common context variables
    context['generated_at'] = datetime.now()
    context['company_name'] = 'Piston Paneli'

    # Render the template with the context
    html_string = render_to_string(template_name, context)

    # Create a temporary file to store the PDF
    with tempfile.NamedTemporaryFile(delete=False) as output:
        # Generate the PDF
        HTML(string=html_string).write_pdf(
            output,
            stylesheets=[
                CSS(string='@page { size: A4; margin: 1cm }')
            ]
        )

    # Read the PDF from the temporary file
    with open(output.name, 'rb') as f:
        pdf = f.read()

    # Delete the temporary file
    os.unlink(output.name)

    # Create the HTTP response with the PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response

def generate_invoice_pdf(siparis):
    """
    Generate a PDF invoice for an order.

    Args:
        siparis: The Siparis object to generate an invoice for

    Returns:
        HttpResponse: A response with the PDF invoice
    """
    # Calculate the total amount
    total_amount = siparis.toplam_fiyat

    # Get all payments for this order
    payments = siparis.odemeler.all()

    # Get all materials used for this order
    materials = siparis.kullanilan_malzemeler.all()

    # Create the context for the template
    context = {
        'siparis': siparis,
        'musteri': siparis.musteri,
        'payments': payments,
        'materials': materials,
        'total_amount': total_amount,
        'paid_amount': siparis.odenen_miktar,
        'remaining_amount': siparis.kalan_odeme(),
    }

    # Generate the PDF
    return generate_pdf('invoice_pdf.html', context, f'fatura_{siparis.id}.pdf')

def generate_report_pdf(rapor):
    """
    Generate a PDF report.

    Args:
        rapor: The Rapor object to generate a PDF for

    Returns:
        HttpResponse: A response with the PDF report
    """
    # Get all orders in the report period
    from .models import Siparis
    siparisler = Siparis.objects.filter(
        tarih__gte=rapor.baslangic_tarihi,
        tarih__lte=rapor.bitis_tarihi
    ).select_related('musteri')

    # Create the context for the template
    context = {
        'rapor': rapor,
        'siparisler': siparisler,
    }

    # Generate the PDF
    return generate_pdf('report_pdf.html', context, f'rapor_{rapor.id}.pdf')

def send_email(subject, message, recipient_list, html_message=None, attachments=None):
    """
    Send an email with optional HTML content and attachments.

    Args:
        subject (str): Email subject
        message (str): Plain text message
        recipient_list (list): List of recipient email addresses
        html_message (str, optional): HTML version of the message
        attachments (list, optional): List of attachments, each as (filename, content, mimetype)

    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    try:
        if html_message:
            # If HTML message is provided, send a multipart email
            email = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=recipient_list
            )
            email.attach_alternative(html_message, "text/html")
        else:
            # Otherwise, send a plain text email
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=recipient_list
            )

        # Add attachments if provided
        if attachments:
            for attachment in attachments:
                email.attach(*attachment)

        # Send the email
        email.send(fail_silently=False)
        return True
    except Exception as e:
        # Log the error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error sending email: {str(e)}")
        return False

def send_order_status_notification(siparis):
    """
    Send a notification email when an order's status changes.

    Args:
        siparis: The Siparis object whose status has changed

    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    # Get the customer's email (assuming it's stored in the address field)
    # In a real application, you would have a dedicated email field
    recipient = settings.ADMIN_EMAIL  # Fallback to admin email

    # Create the subject and message
    subject = f"Sipariş Durumu Güncellendi: #{siparis.id} - {siparis.urun_tipi}"

    # Plain text message
    message = f"""
Sayın {siparis.musteri.isim},

Siparişinizin durumu güncellendi.

Sipariş Bilgileri:
- Sipariş No: {siparis.id}
- Ürün: {siparis.urun_tipi}
- Yeni Durum: {siparis.get_durum_display()}
- Güncelleme Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}

Sorularınız için lütfen bizimle iletişime geçin.

Saygılarımızla,
Piston Paneli Ekibi
"""

    # HTML message
    html_message = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #3498db; color: white; padding: 10px 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .footer {{ background-color: #f5f5f5; padding: 10px 20px; text-align: center; font-size: 0.8em; color: #777; }}
        .status {{ display: inline-block; padding: 5px 10px; border-radius: 3px; font-weight: bold; color: white; }}
        .status-beklemede {{ background-color: #f39c12; }}
        .status-uretimde {{ background-color: #3498db; }}
        .status-tamamlandi {{ background-color: #2ecc71; }}
        .status-teslim_edildi {{ background-color: #27ae60; }}
        .status-iptal_edildi {{ background-color: #e74c3c; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Sipariş Durumu Güncellendi</h1>
        </div>
        <div class="content">
            <p>Sayın <strong>{siparis.musteri.isim}</strong>,</p>
            <p>Siparişinizin durumu güncellendi.</p>

            <h2>Sipariş Bilgileri:</h2>
            <ul>
                <li><strong>Sipariş No:</strong> {siparis.id}</li>
                <li><strong>Ürün:</strong> {siparis.urun_tipi}</li>
                <li><strong>Yeni Durum:</strong> <span class="status status-{siparis.durum}">{siparis.get_durum_display()}</span></li>
                <li><strong>Güncelleme Tarihi:</strong> {datetime.now().strftime('%d.%m.%Y %H:%M')}</li>
            </ul>

            <p>Sorularınız için lütfen bizimle iletişime geçin.</p>
        </div>
        <div class="footer">
            <p>Saygılarımızla,<br>Piston Paneli Ekibi</p>
        </div>
    </div>
</body>
</html>
"""

    # Send the email
    return send_email(subject, message, [recipient], html_message)

def send_payment_notification(odeme):
    """
    Send a notification email when a payment is received.

    Args:
        odeme: The Odeme object representing the payment

    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    # Get the customer's email (assuming it's stored in the address field)
    # In a real application, you would have a dedicated email field
    recipient = settings.ADMIN_EMAIL  # Fallback to admin email

    siparis = odeme.siparis
    musteri = siparis.musteri

    # Create the subject and message
    subject = f"Ödeme Alındı: #{siparis.id} - {siparis.urun_tipi}"

    # Plain text message
    message = f"""
Sayın {musteri.isim},

Siparişiniz için ödemeniz alındı.

Ödeme Bilgileri:
- Sipariş No: {siparis.id}
- Ürün: {siparis.urun_tipi}
- Ödeme Miktarı: {odeme.miktar} TL
- Ödeme Tarihi: {odeme.tarih.strftime('%d.%m.%Y %H:%M')}
- Açıklama: {odeme.aciklama}

Toplam Sipariş Tutarı: {siparis.toplam_fiyat} TL
Toplam Ödenen: {siparis.odenen_miktar} TL
Kalan Ödeme: {siparis.kalan_odeme()} TL

Sorularınız için lütfen bizimle iletişime geçin.

Saygılarımızla,
Piston Paneli Ekibi
"""

    # HTML message
    html_message = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #2ecc71; color: white; padding: 10px 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .footer {{ background-color: #f5f5f5; padding: 10px 20px; text-align: center; font-size: 0.8em; color: #777; }}
        .payment-info {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .total-row {{ display: flex; justify-content: space-between; margin-bottom: 5px; }}
        .total-label {{ font-weight: bold; }}
        .grand-total {{ font-size: 1.2em; font-weight: bold; color: #2ecc71; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Ödeme Alındı</h1>
        </div>
        <div class="content">
            <p>Sayın <strong>{musteri.isim}</strong>,</p>
            <p>Siparişiniz için ödemeniz alındı.</p>

            <div class="payment-info">
                <h2>Ödeme Bilgileri:</h2>
                <ul>
                    <li><strong>Sipariş No:</strong> {siparis.id}</li>
                    <li><strong>Ürün:</strong> {siparis.urun_tipi}</li>
                    <li><strong>Ödeme Miktarı:</strong> {odeme.miktar} TL</li>
                    <li><strong>Ödeme Tarihi:</strong> {odeme.tarih.strftime('%d.%m.%Y %H:%M')}</li>
                    <li><strong>Açıklama:</strong> {odeme.aciklama}</li>
                </ul>
            </div>

            <div class="total-section">
                <div class="total-row">
                    <span class="total-label">Toplam Sipariş Tutarı:</span>
                    <span>{siparis.toplam_fiyat} TL</span>
                </div>
                <div class="total-row">
                    <span class="total-label">Toplam Ödenen:</span>
                    <span>{siparis.odenen_miktar} TL</span>
                </div>
                <div class="total-row grand-total">
                    <span class="total-label">Kalan Ödeme:</span>
                    <span>{siparis.kalan_odeme()} TL</span>
                </div>
            </div>

            <p>Sorularınız için lütfen bizimle iletişime geçin.</p>
        </div>
        <div class="footer">
            <p>Saygılarımızla,<br>Piston Paneli Ekibi</p>
        </div>
    </div>
</body>
</html>
"""

    # Send the email
    return send_email(subject, message, [recipient], html_message)

def send_critical_stock_alert(malzeme):
    """
    Send an alert email when a material's stock level falls below the minimum threshold.

    Args:
        malzeme: The Malzeme object with critical stock level

    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    # Send to admin email
    recipient = settings.ADMIN_EMAIL

    # Create the subject and message
    subject = f"Kritik Stok Uyarısı: {malzeme.ad}"

    # Plain text message
    message = f"""
KRİTİK STOK UYARISI

Aşağıdaki malzemenin stok seviyesi kritik seviyenin altına düşmüştür:

Malzeme Bilgileri:
- Malzeme Adı: {malzeme.ad}
- Malzeme Türü: {malzeme.get_tur_display()}
- Mevcut Stok: {malzeme.stok_miktari} {malzeme.get_birim_display()}
- Minimum Stok: {malzeme.minimum_stok} {malzeme.get_birim_display()}

Lütfen en kısa sürede stok takviyesi yapın.

Piston Paneli Stok Yönetim Sistemi
"""

    # HTML message
    html_message = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #e74c3c; color: white; padding: 10px 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .footer {{ background-color: #f5f5f5; padding: 10px 20px; text-align: center; font-size: 0.8em; color: #777; }}
        .alert {{ background-color: #ffecec; border-left: 4px solid #e74c3c; padding: 15px; margin-bottom: 20px; }}
        .stock-info {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .critical {{ color: #e74c3c; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Kritik Stok Uyarısı</h1>
        </div>
        <div class="content">
            <div class="alert">
                <p>Aşağıdaki malzemenin stok seviyesi kritik seviyenin altına düşmüştür:</p>
            </div>

            <div class="stock-info">
                <h2>Malzeme Bilgileri:</h2>
                <ul>
                    <li><strong>Malzeme Adı:</strong> {malzeme.ad}</li>
                    <li><strong>Malzeme Türü:</strong> {malzeme.get_tur_display()}</li>
                    <li><strong>Mevcut Stok:</strong> <span class="critical">{malzeme.stok_miktari}</span> {malzeme.get_birim_display()}</li>
                    <li><strong>Minimum Stok:</strong> {malzeme.minimum_stok} {malzeme.get_birim_display()}</li>
                </ul>
            </div>

            <p>Lütfen en kısa sürede stok takviyesi yapın.</p>
        </div>
        <div class="footer">
            <p>Piston Paneli Stok Yönetim Sistemi</p>
        </div>
    </div>
</body>
</html>
"""

    # Send the email
    return send_email(subject, message, [recipient], html_message)
