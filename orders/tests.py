import json
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, override_settings
from django.urls import reverse
from products.models import Category, Product
from .models import Order
from .services import create_order, sepay_checkout_data, sepay_checkout_url


class SePayPaymentTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name='Cà phê', slug='ca-phe')
        self.product = Product.objects.create(category=category, name='Cà phê test', slug='ca-phe-test', description='Test', price=120000)
        self.order = create_order(
            user=AnonymousUser(),
            summary={'items': [{'product': self.product, 'quantity': 1, 'subtotal': 120000}], 'subtotal': 120000, 'shipping': 30000, 'total': 150000, 'voucher': None},
            data={'name': 'Bean', 'email': 'bean@example.com', 'phone': '0900000000', 'address': 'Hà Nội', 'payment': Order.SEPAY},
        )

    @override_settings(SEPAY_GATEWAY_MERCHANT_ID='SP-TEST-123', SEPAY_GATEWAY_SECRET_KEY='test-secret', SEPAY_GATEWAY_ENV='sandbox')
    def test_checkout_payload_contains_signed_payment_details(self):
        payload = sepay_checkout_data(self.order)
        self.assertEqual(payload['merchant'], 'SP-TEST-123')
        self.assertEqual(payload['order_amount'], str(self.order.total))
        self.assertEqual(payload['order_invoice_number'], self.order.code)
        self.assertTrue(payload['signature'])
        self.assertEqual(sepay_checkout_url(), 'https://pay-sandbox.sepay.vn/v1/checkout/init')

    @override_settings(SEPAY_GATEWAY_SECRET_KEY='demo-secret')
    def test_ipn_marks_matching_order_paid(self):
        payload = {'timestamp': 1760000000, 'notification_type': 'ORDER_PAID', 'order': {'order_invoice_number': self.order.code}, 'transaction': {'transaction_id': 'FT-91', 'transaction_amount': str(self.order.total)}}
        body = json.dumps(payload).encode()
        response = self.client.post(reverse('sepay-webhook'), data=body, content_type='application/json', HTTP_X_SECRET_KEY='demo-secret')
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, Order.PAID)

# Create your tests here.
