from django.test import TestCase
from django.urls import reverse
from .models import Category, Product


class ProductCatalogueTests(TestCase):
    def setUp(self):
        coffee = Category.objects.create(name='Cà phê hạt', slug='ca-phe-hat')
        tools = Category.objects.create(name='Dụng cụ', slug='dung-cu')
        Product.objects.create(category=coffee, name='Rang đậm', slug='rang-dam', description='Đậm đà', price=150000, roast_level='dark')
        Product.objects.create(category=tools, name='V60', slug='v60', description='Pour over', price=320000, roast_level='light')

    def test_category_filter_returns_matching_product(self):
        response = self.client.get(reverse('products:list'), {'category': 'ca-phe-hat'})
        self.assertContains(response, 'Rang đậm')
        self.assertNotContains(response, '>V60<')

    def test_product_detail_is_public(self):
        response = self.client.get(reverse('products:detail', args=['rang-dam']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Thêm vào giỏ hàng')

    def test_catalogue_api_filters_by_category(self):
        response = self.client.get('/api/products/?category=ca-phe-hat')
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]['slug'], 'rang-dam')

    def test_catalogue_api_returns_product_detail(self):
        response = self.client.get('/api/products/rang-dam/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['category_slug'], 'ca-phe-hat')

# Create your tests here.
