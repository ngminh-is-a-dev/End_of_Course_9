from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from products.models import Category, Product
from promotions.models import Voucher


class SessionCartTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name='Cà phê', slug='ca-phe')
        self.product = Product.objects.create(category=category, name='Mộc', slug='moc', description='Cà phê', price=120000)

    def test_add_product_to_session_cart(self):
        response = self.client.post(reverse('cart:add', args=[self.product.id]), {'quantity': 2, 'next': reverse('cart:detail')})
        self.assertRedirects(response, reverse('cart:detail'))
        cart_page = self.client.get(reverse('cart:detail'))
        self.assertContains(cart_page, '240000đ')

    def test_new_account_receives_and_can_apply_freeship_voucher(self):
        user = User.objects.create_user(username='beanfan', password='safe-pass-123')
        voucher = Voucher.objects.get(user=user)
        self.client.force_login(user)
        self.client.post(reverse('cart:add', args=[self.product.id]), {'quantity': 1, 'next': reverse('cart:detail')})
        response = self.client.post(reverse('cart:apply-voucher'), {'code': voucher.code}, follow=True)
        self.assertContains(response, 'Miễn phí')
        self.assertContains(response, voucher.code)

# Create your tests here.
