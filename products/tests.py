from django.test import Client, TestCase
from django.urls import reverse
from .models import Category, Product, ProductReview


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


class ProductReviewModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Cà phê', slug='ca-phe-review')
        self.product = Product.objects.create(
            category=self.category,
            name='Arabica',
            slug='arabica-review',
            description='Cà phê thơm',
            price=125000,
        )

    def _review_model(self):
        from django.apps import apps

        model = next((model for model in apps.get_models() if model.__name__ == 'ProductReview'), None)
        self.assertIsNotNone(model, 'ProductReview model has not been added yet')
        return model

    def test_rating_boundaries_and_optional_content(self):
        self._review_model()
        from products.forms import ProductReviewForm

        self.assertTrue(ProductReviewForm(data={'rating': '1', 'content': ''}).is_valid())
        self.assertTrue(ProductReviewForm(data={'rating': '5', 'content': 'Great coffee'}).is_valid())
        self.assertFalse(ProductReviewForm(data={'rating': '0', 'content': ''}).is_valid())
        self.assertFalse(ProductReviewForm(data={'rating': '6', 'content': ''}).is_valid())
        self.assertFalse(ProductReviewForm(data={'rating': '5', 'content': 'x' * 2001}).is_valid())

    def test_database_enforces_one_review_per_user_and_product(self):
        from django.contrib.auth import get_user_model
        from django.db import IntegrityError, transaction

        review_model = self._review_model()
        user = get_user_model().objects.create_user(username='reviewer', password='pass12345')
        review_model.objects.create(product=self.product, user=user, rating=4, content='Good')

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                review_model.objects.create(product=self.product, user=user, rating=5, content='Again')

    def test_review_model_is_registered_in_admin(self):
        from django.contrib import admin

        review_model = self._review_model()

        self.assertIn(review_model, admin.site._registry)


class ProductReviewSubmissionTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Review coffee', slug='review-coffee')
        self.product = Product.objects.create(
            category=self.category,
            name='Review Arabica',
            slug='review-arabica',
            description='Coffee for reviews',
            price=125000,
        )

    def _new_user(self, username):
        from django.contrib.auth import get_user_model

        return get_user_model().objects.create_user(username=username, password='pass12345')

    def test_guest_post_redirects_to_login_and_returns_to_product(self):
        response = self.client.post(reverse('products:detail', args=[self.product.slug]), {
            'rating': '5',
            'content': 'Great',
        })

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('products:detail', args=[self.product.slug])}",
        )
        self.assertFalse(ProductReview.objects.exists())

    def test_authenticated_user_creates_review_for_self(self):
        user = self._new_user('new-reviewer')
        self.client.force_login(user)

        response = self.client.post(reverse('products:detail', args=[self.product.slug]), {
            'rating': '4',
            'content': 'Tastes balanced',
            'user': '99999',
        })

        self.assertRedirects(response, reverse('products:detail', args=[self.product.slug]))
        review = ProductReview.objects.get(product=self.product)
        self.assertEqual(review.user, user)
        self.assertEqual(review.rating, 4)

    def test_user_edits_existing_review_instead_of_creating_duplicate(self):
        user = self._new_user('existing-reviewer')
        review = ProductReview.objects.create(product=self.product, user=user, rating=2, content='Old')
        self.client.force_login(user)

        response = self.client.post(reverse('products:detail', args=[self.product.slug]), {
            'rating': '5',
            'content': 'Updated',
        })

        self.assertRedirects(response, reverse('products:detail', args=[self.product.slug]))
        review.refresh_from_db()
        self.assertEqual(ProductReview.objects.filter(product=self.product, user=user).count(), 1)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.content, 'Updated')

    def test_post_cannot_change_another_users_review(self):
        owner = self._new_user('review-owner')
        attacker = self._new_user('review-attacker')
        review = ProductReview.objects.create(product=self.product, user=owner, rating=2, content='Owner review')
        self.client.force_login(attacker)

        self.client.post(reverse('products:detail', args=[self.product.slug]), {
            'rating': '5',
            'content': 'Attempted overwrite',
            'user': str(owner.pk),
        })

        review.refresh_from_db()
        self.assertEqual(review.rating, 2)
        self.assertEqual(review.content, 'Owner review')
        self.assertTrue(ProductReview.objects.filter(product=self.product, user=attacker).exists())

    def test_product_context_aggregates_public_reviews_and_empty_state(self):
        from django.db.models import Avg

        response = self.client.get(reverse('products:detail', args=[self.product.slug]))
        self.assertEqual(response.context['review_count'], 0)
        self.assertIsNone(response.context['review_average'])
        one = self._new_user('average-one')
        two = self._new_user('average-two')
        ProductReview.objects.create(product=self.product, user=one, rating=3, content='Okay')
        ProductReview.objects.create(product=self.product, user=two, rating=5, content='Excellent')

        response = self.client.get(reverse('products:detail', args=[self.product.slug]))

        self.assertEqual(response.context['review_count'], 2)
        self.assertEqual(response.context['review_average'], 4)
        self.assertEqual(response.context['reviews'].count(), 2)

    def test_invalid_review_post_does_not_create_row(self):
        user = self._new_user('invalid-reviewer')
        self.client.force_login(user)

        response = self.client.post(reverse('products:detail', args=[self.product.slug]), {
            'rating': '6',
            'content': 'x' * 2001,
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['review_form'].errors)
        self.assertFalse(ProductReview.objects.exists())


class ProductReviewDisplayTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Display coffee', slug='display-coffee')
        self.product = Product.objects.create(
            category=self.category,
            name='Display Arabica',
            slug='display-arabica',
            description='Coffee for display tests',
            price=125000,
        )

    def test_empty_review_section_shows_zero_and_prompt(self):
        response = self.client.get(reverse('products:detail', args=[self.product.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '0 đánh giá')
        self.assertContains(response, 'Chưa có đánh giá')
        self.assertContains(response, 'Đăng nhập để đánh giá')

    def test_reviews_are_public_and_render_author_rating_and_content(self):
        from django.contrib.auth import get_user_model

        user = get_user_model().objects.create_user(username='public-reviewer', password='pass12345')
        ProductReview.objects.create(product=self.product, user=user, rating=4, content='Rất thơm & ngon')

        response = self.client.get(reverse('products:detail', args=[self.product.slug]))

        self.assertContains(response, '4,0/5')
        self.assertContains(response, '1 đánh giá')
        self.assertContains(response, 'public-reviewer')
        self.assertContains(response, 'Rất thơm &amp; ngon')

    def test_signed_in_user_sees_review_form_and_edit_label(self):
        from django.contrib.auth import get_user_model

        user = get_user_model().objects.create_user(username='form-reviewer', password='pass12345')
        ProductReview.objects.create(product=self.product, user=user, rating=3, content='Okay')
        self.client.force_login(user)

        response = self.client.get(reverse('products:detail', args=[self.product.slug]))

        self.assertContains(response, 'name="rating"')
        self.assertContains(response, 'Cập nhật đánh giá')
        self.assertContains(response, 'value="3"')
        self.assertContains(response, 'checked')

    def test_product_has_product_open_graph_and_social_share_controls(self):
        response = self.client.get(reverse('products:detail', args=[self.product.slug]))

        self.assertContains(response, 'property="og:title" content="Display Arabica | Bean &amp; Leaf"')
        self.assertContains(response, 'property="og:description" content="Coffee for display tests"')
        self.assertContains(response, 'property="og:url" content="http://testserver/products/display-arabica/"')
        self.assertContains(response, 'property="og:type" content="product"')
        self.assertContains(response, 'Chia sẻ Facebook')
        self.assertContains(response, 'Sao chép liên kết để chia sẻ trên Zalo')
        self.assertContains(response, 'Sao chép liên kết')
        self.assertContains(response, 'role="status" aria-live="polite"')
        self.assertContains(response, 'data-copy-url="http://testserver/products/display-arabica/"')
        self.assertContains(
            response,
            'href="https://www.facebook.com/sharer/sharer.php?u=http%3A%2F%2Ftestserver%2Fproducts%2Fdisplay-arabica%2F"',
        )
        self.assertContains(response, 'property="og:image" content="http://testserver/static/images/coffee-hero.png"')

    def test_product_open_graph_escapes_and_bounds_description(self):
        from html import unescape
        import re

        self.product.name = '<Coffee "special">'
        self.product.description = '<script>alert("x")</script>' + (' coffee' * 50)
        self.product.save()

        response = self.client.get(reverse('products:detail', args=[self.product.slug]))
        content = response.content.decode()
        description = re.search(r'property="og:description" content="([^"]*)"', content).group(1)

        self.assertContains(response, 'property="og:title" content="&lt;Coffee &quot;special&quot;&gt; | Bean &amp; Leaf"')
        self.assertIn('&lt;script&gt;', description)
        self.assertLessEqual(len(unescape(description)), 200)

    def test_zalo_official_share_widget_uses_configured_oa_id(self):
        from django.test import override_settings

        with override_settings(ZALO_OA_ID='123456789'):
            response = self.client.get(reverse('products:detail', args=[self.product.slug]))

        self.assertContains(response, 'class="zalo-share-button"')
        self.assertContains(response, 'data-oaid="123456789"')
        self.assertContains(response, 'src="https://sp.zalo.me/plugins/sdk.js"')

class ProductReviewSecurityTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model

        category = Category.objects.create(name='Security coffee', slug='security-coffee')
        self.product = Product.objects.create(
            category=category,
            name='Security Arabica',
            slug='security-arabica',
            description='Coffee for security checks',
            price=125000,
        )
        self.user = get_user_model().objects.create_user(username='security-reviewer')
        self.url = reverse('products:detail', args=[self.product.slug])

    def test_review_post_requires_valid_csrf_token_before_creating_review(self):
        import re

        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        page = client.get(self.url)
        self.assertEqual(page.status_code, 200)
        token = re.search(
            r'name="csrfmiddlewaretoken" value="([^"]+)"', page.content.decode()
        ).group(1)
        data = {'rating': '5', 'content': 'Valid review'}

        rejected = client.post(self.url, data)

        self.assertEqual(rejected.status_code, 403)
        self.assertFalse(ProductReview.objects.exists())

        accepted = client.post(self.url, {**data, 'csrfmiddlewaretoken': token})

        self.assertRedirects(accepted, self.url)
        review = ProductReview.objects.get(product=self.product, user=self.user)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.content, 'Valid review')

    def test_public_review_escapes_untrusted_html_and_preserves_line_breaks(self):
        ProductReview.objects.create(
            product=self.product,
            user=self.user,
            rating=4,
            content='<script>alert("xss")</script>\n<img src=x onerror=alert(1)>',
        )

        response = self.client.get(self.url)

        self.assertContains(response, '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;')
        self.assertContains(response, '<br>&lt;img src=x onerror=alert(1)&gt;')
        self.assertNotContains(response, '<script>alert("xss")</script>')
        self.assertNotContains(response, '<img src=x onerror=alert(1)>')
