import hashlib
import hmac
import base64
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode
from django.conf import settings
from django.utils import timezone
from .models import Order, OrderItem


def _is_sufficient_amount(value, minimum):
    try:
        return Decimal(str(value)) >= Decimal(minimum)
    except (InvalidOperation, TypeError, ValueError):
        return False


def create_order(*, user, summary, data):
    order = Order.objects.create(
        user=user if user.is_authenticated else None,
        customer_name=data['name'],
        email=data['email'],
        phone=data['phone'],
        address=data['address'],
        subtotal=summary['subtotal'],
        shipping_fee=summary['shipping'],
        total=summary['total'],
        voucher=summary['voucher'],
        payment_method=data['payment'],
    )
    OrderItem.objects.bulk_create([
        OrderItem(order=order, product=item['product'], product_name=item['product'].name, unit_price=item['product'].price, quantity=item['quantity'])
        for item in summary['items']
    ])
    return order


def sepay_checkout_data(order):
    """Prepare SePay gateway fields in the order required by the signature spec."""
    fields = {
        'order_amount': str(order.total),
        'merchant': settings.SEPAY_GATEWAY_MERCHANT_ID,
        'currency': 'VND',
        'operation': 'PURCHASE',
        'order_description': f'Thanh toan don hang {order.code}',
        'order_invoice_number': order.code,
        'payment_method': 'BANK_TRANSFER',
        'success_url': f'{settings.SITE_URL}/checkout/success/{order.code}/',
        'error_url': f'{settings.SITE_URL}/checkout/sepay/{order.code}/error/',
        'cancel_url': f'{settings.SITE_URL}/checkout/sepay/{order.code}/cancel/',
    }
    if order.user_id:
        fields['customer_id'] = str(order.user_id)
    signed_names = ('order_amount', 'merchant', 'currency', 'operation', 'order_description', 'order_invoice_number', 'customer_id', 'payment_method', 'success_url', 'error_url', 'cancel_url')
    signed_string = ','.join(f'{name}={fields[name]}' for name in signed_names if name in fields)
    digest = hmac.new(settings.SEPAY_GATEWAY_SECRET_KEY.encode(), signed_string.encode(), hashlib.sha256).digest()
    fields['signature'] = base64.b64encode(digest).decode()
    return fields


def sepay_checkout_url():
    host = 'https://pay-sandbox.sepay.vn' if settings.SEPAY_GATEWAY_ENV == 'sandbox' else 'https://pay.sepay.vn'
    return f'{host}/v1/checkout/init'


def verify_webhook(request):
    gateway_secret = settings.SEPAY_GATEWAY_SECRET_KEY
    if gateway_secret:
        gateway_header = request.headers.get('X-Secret-Key')
        if gateway_header:
            return hmac.compare_digest(gateway_header, gateway_secret)
    raw_body = request.body
    secret = settings.SEPAY_WEBHOOK_SECRET
    api_key = settings.SEPAY_WEBHOOK_API_KEY
    if secret:
        timestamp = request.headers.get('X-SePay-Timestamp', '')
        signature = request.headers.get('X-SePay-Signature', '')
        try:
            if abs(timezone.now().timestamp() - int(timestamp)) > 300:
                return False
        except ValueError:
            return False
        digest = hmac.new(secret.encode(), f'{timestamp}.'.encode() + raw_body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(f'sha256={digest}', signature)
    if api_key:
        return hmac.compare_digest(request.headers.get('Authorization', ''), f'Apikey {api_key}')
    return False


def mark_order_paid(payload):
    if payload.get('notification_type') == 'ORDER_PAID':
        order_data = payload.get('order', {})
        transaction = payload.get('transaction', {})
        code = str(order_data.get('order_invoice_number', '')).upper()
        transaction_id = str(transaction.get('transaction_id') or transaction.get('id') or '')
        order = Order.objects.filter(code=code, payment_method=Order.SEPAY, payment_status=Order.PENDING).first()
        if not order or not _is_sufficient_amount(transaction.get('transaction_amount', 0), order.total):
            return None
        if transaction_id and Order.objects.filter(transaction_id=transaction_id).exists():
            return None
        order.payment_status = Order.PAID
        order.transaction_id = transaction_id or None
        order.paid_at = timezone.now()
        order.save(update_fields=['payment_status', 'transaction_id', 'paid_at'])
        if order.voucher:
            order.voucher.is_used = True
            order.voucher.save(update_fields=['is_used'])
        return order
    code = str(payload.get('code', '')).upper()
    content = str(payload.get('content', '')).upper()
    order = Order.objects.filter(code=code, payment_method=Order.SEPAY, payment_status=Order.PENDING).first()
    if not order:
        order = next((item for item in Order.objects.filter(payment_method=Order.SEPAY, payment_status=Order.PENDING) if item.code in content), None)
    if not order or payload.get('transferType') != 'in' or not _is_sufficient_amount(payload.get('transferAmount', 0), order.total):
        return None
    transaction_id = str(payload.get('referenceCode') or payload.get('id') or '')
    if transaction_id and Order.objects.filter(transaction_id=transaction_id).exists():
        return None
    order.payment_status = Order.PAID
    order.transaction_id = transaction_id or None
    order.paid_at = timezone.now()
    order.save(update_fields=['payment_status', 'transaction_id', 'paid_at'])
    if order.voucher:
        order.voucher.is_used = True
        order.voucher.save(update_fields=['is_used'])
    return order
