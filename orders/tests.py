from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .admin import OrderAdmin
from .models import Order
from .services import create_order


class OrderDeliveryStatusTests(TestCase):
    def test_new_order_starts_in_packing(self):
        user = get_user_model().objects.create_user(username='order-user', password='pass12345')

        order = Order.objects.create(
            user=user,
            customer_name='Order User',
            email='order@example.com',
            phone='0900000000',
            address='1 Test Street',
            subtotal=100,
            shipping_fee=0,
            total=100,
            payment_method=Order.COD,
        )

        self.assertEqual(order.delivery_status, Order.PACKING)

    def test_delivery_statuses_have_required_labels(self):
        self.assertEqual(
            Order.DELIVERY_STATUS_CHOICES,
            [
                (Order.PACKING, 'Đang đóng gói'),
                (Order.SHIPPING, 'Đang giao'),
                (Order.DELIVERED, 'Đã giao'),
            ],
        )

    def test_admin_can_quick_edit_delivery_status(self):
        self.assertIn('delivery_status', OrderAdmin.list_editable)


class CheckoutDeliveryStatusTests(TestCase):
    def test_success_page_shows_order_confirmation_and_delivery_status(self):
        order = Order.objects.create(
            user=None,
            customer_name='Guest Customer',
            email='guest@example.com',
            phone='0900000000',
            address='1 Guest Street',
            subtotal=100,
            shipping_fee=0,
            total=100,
            payment_method=Order.COD,
        )

        response = self.client.get(reverse('checkout-success', kwargs={'code': order.code}))

        self.assertContains(response, 'Đặt hàng thành công')
        self.assertContains(response, 'Đang đóng gói')

    def test_guest_order_creation_remains_cash_on_delivery(self):
        from django.contrib.auth.models import AnonymousUser

        order = create_order(
            user=AnonymousUser(),
            summary={'subtotal': 100, 'shipping': 0, 'total': 100, 'voucher': None, 'items': []},
            data={
                'name': 'Guest Customer',
                'email': 'guest@example.com',
                'phone': '0900000000',
                'address': '1 Guest Street',
                'payment': Order.COD,
            },
        )

        self.assertIsNone(order.user)
        self.assertEqual(order.payment_method, Order.COD)
        self.assertEqual(order.delivery_status, Order.PACKING)
