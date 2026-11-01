from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from products.models import Category, Product
from cart.services import SESSION_KEY

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


class CheckoutInputValidationTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name='Checkout coffee', slug='checkout-coffee')
        self.product = Product.objects.create(
            category=category,
            name='Checkout blend',
            slug='checkout-blend',
            description='Checkout validation fixture',
            price=100000,
        )
        session = self.client.session
        session[SESSION_KEY] = {str(self.product.pk): 1}
        session.save()
        self.checkout_url = reverse('checkout')
        self.valid_data = {
            'name': 'Test Customer',
            'phone': '0900000000',
            'email': 'customer@example.com',
            'address': '1 Test Street',
            'payment': Order.COD,
        }

    def test_checkout_rejects_malformed_email_without_creating_order(self):
        response = self.client.post(self.checkout_url, {
            **self.valid_data,
            'email': 'not-an-email',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Email không hợp lệ')
        self.assertFalse(Order.objects.exists())

    def test_checkout_rejects_values_longer_than_order_fields(self):
        response = self.client.post(self.checkout_url, {
            **self.valid_data,
            'name': 'x' * 121,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Thông tin giao hàng vượt quá độ dài cho phép')
        self.assertFalse(Order.objects.exists())

    def test_checkout_rejects_quantity_above_current_stock(self):
        self.product.stock = 1
        self.product.save(update_fields=['stock'])
        session = self.client.session
        session[SESSION_KEY] = {str(self.product.pk): 2}
        session.save()

        response = self.client.post(self.checkout_url, self.valid_data, follow=True)

        self.assertContains(response, 'Số lượng sản phẩm vượt quá tồn kho hiện tại')
        self.assertFalse(Order.objects.exists())
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 1)

    def test_successful_checkout_decrements_stock(self):
        self.product.stock = 3
        self.product.save(update_fields=['stock'])

        response = self.client.post(self.checkout_url, self.valid_data)

        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)
        self.assertEqual(Order.objects.count(), 1)
