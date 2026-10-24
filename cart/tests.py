from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.db import connection
from django.test.utils import CaptureQueriesContext
from products.models import Category, Product
from promotions.models import Voucher
from .services import SESSION_KEY


class SessionCartTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name='Cà phê', slug='ca-phe')
        self.product = Product.objects.create(category=category, name='Mộc', slug='moc', description='Cà phê', price=120000)

    def test_add_product_to_session_cart(self):
        response = self.client.post(reverse('cart:add', args=[self.product.id]), {'quantity': 2, 'next': reverse('cart:detail')})
        self.assertRedirects(response, reverse('cart:detail'))
        cart_page = self.client.get(reverse('cart:detail'))
        self.assertContains(cart_page, '240000đ')

    def test_cart_page_queries_do_not_grow_when_product_categories_render(self):
        products = [self.product]
        for index in range(2):
            category = Category.objects.create(name=f'Cart category {index}', slug=f'cart-category-{index}')
            products.append(Product.objects.create(
                category=category, name=f'Cart product {index}', slug=f'cart-product-{index}',
                description='Query regression fixture', price=10000,
            ))

        measurements = []
        for product_count in (1, 3):
            session = self.client.session
            session[SESSION_KEY] = {str(product.pk): 2 for product in products[:product_count]}
            session.save()

            with CaptureQueriesContext(connection) as queries:
                response = self.client.get(reverse('cart:detail'))

            self.assertEqual(response.status_code, 200)
            for product in products[:product_count]:
                self.assertContains(response, product.name)
                self.assertContains(response, product.category.name)
            self.assertEqual(len(response.context['items']), product_count)
            self.assertTrue(all(item['quantity'] == 2 for item in response.context['items']))
            self.assertEqual(response.context['subtotal'], 240000 if product_count == 1 else 280000)
            measurements.append({
                'total': len(queries),
                'category': sum('FROM "products_category"' in query['sql'] for query in queries),
            })

        self.assertEqual(measurements[0], measurements[1], msg=f'Cart queries (1, 3 products): {measurements}')
        self.assertEqual(measurements[0]['category'], 0)

    def test_new_account_receives_and_can_apply_freeship_voucher(self):
        user = User.objects.create_user(username='beanfan', password='safe-pass-123')
        voucher = Voucher.objects.get(user=user)
        self.client.force_login(user)
        self.client.post(reverse('cart:add', args=[self.product.id]), {'quantity': 1, 'next': reverse('cart:detail')})
        response = self.client.post(reverse('cart:apply-voucher'), {'code': voucher.code}, follow=True)
        self.assertContains(response, 'Miễn phí')
        self.assertContains(response, voucher.code)

# Create your tests here.
