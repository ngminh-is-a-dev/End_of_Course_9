from io import BytesIO
import tempfile
from datetime import datetime, timedelta
from io import StringIO
from unittest.mock import patch

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from PIL import Image

from orders.models import Order, OrderItem
from products.models import Category, Product
from .models import LoginHistory


class ProfileAndLoginHistoryTests(TestCase):
    def test_new_user_gets_a_profile(self):
        model_names = {model.__name__ for model in apps.get_models()}
        self.assertIn('UserProfile', model_names)

        user = get_user_model().objects.create_user(username='new-user', password='pass12345')

        self.assertTrue(user.profile.pk)
        self.assertFalse(user.profile.avatar)

    def test_successful_login_records_ip_and_timestamp(self):
        model_names = {model.__name__ for model in apps.get_models()}
        self.assertIn('LoginHistory', model_names)
        user = get_user_model().objects.create_user(username='login-user', password='pass12345')
        login_model = apps.get_model('accounts', 'LoginHistory')

        response = self.client.post(reverse('accounts:login'), {
            'username': 'login-user',
            'password': 'pass12345',
        })

        self.assertEqual(response.status_code, 302)
        history = login_model.objects.get(user=user)
        self.assertEqual(history.ip_address, '127.0.0.1')
        self.assertIsNotNone(history.created_at)

    def test_login_without_remote_addr_stores_no_ip(self):
        model_names = {model.__name__ for model in apps.get_models()}
        self.assertIn('LoginHistory', model_names)
        user = get_user_model().objects.create_user(username='no-ip-user', password='pass12345')
        login_model = apps.get_model('accounts', 'LoginHistory')

        from django.contrib.auth.signals import user_logged_in
        from types import SimpleNamespace

        user_logged_in.send(sender=get_user_model(), request=SimpleNamespace(META={}), user=user)

        history = login_model.objects.get(user=user)
        self.assertIsNone(history.ip_address)
        self.assertIsNotNone(history.created_at)


class ProfilePageTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='profile-user', password='pass12345', first_name='', last_name=''
        )

    def _create_order(self, user):
        return Order.objects.create(
            user=user,
            customer_name=user.username,
            email=f'{user.username}@example.com',
            phone='0900000000',
            address='1 Test Street',
            subtotal=100,
            shipping_fee=0,
            total=100,
            payment_method=Order.COD,
        )

    def test_anonymous_user_is_redirected_to_login_with_profile_next(self):
        response = self.client.get('/accounts/profile/')

        self.assertRedirects(response, f"{reverse('accounts:login')}?next=/accounts/profile/")

    def test_profile_prefetches_items_without_querying_unused_products(self):
        category = Category.objects.create(name='Profile category', slug='profile-category')
        product = Product.objects.create(
            category=category, name='Current catalog name', slug='profile-product',
            description='Query regression fixture', price=100,
        )
        self.client.force_login(self.user)
        orders = []
        measurements = []

        for order_count in (1, 3):
            while len(orders) < order_count:
                order = self._create_order(self.user)
                OrderItem.objects.create(
                    order=order, product=product, product_name=f'Purchased name {len(orders)}',
                    unit_price=100, quantity=2,
                )
                orders.append(order)

            with CaptureQueriesContext(connection) as queries:
                response = self.client.get(reverse('accounts:profile'))

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context['orders']), order_count)
            for index, order in enumerate(orders):
                self.assertContains(response, order.code)
                self.assertContains(response, f'Purchased name {index}')
            self.assertContains(response, '× 2', count=order_count)
            self.assertNotContains(response, 'Current catalog name')
            related_counts = {
                'items': sum('FROM "orders_orderitem"' in query['sql'] for query in queries),
                'products': sum('FROM "products_product"' in query['sql'] for query in queries),
            }
            measurements.append({'total': len(queries), **related_counts})
            with self.subTest(order_count=order_count):
                self.assertEqual(related_counts, {'items': 1, 'products': 0}, msg=f'Profile queries: {measurements[-1]}')

        self.assertEqual(measurements[0], measurements[1], msg=f'Profile queries (1, 3 orders): {measurements}')

    def test_profile_shows_username_fallback_and_only_own_orders(self):
        own_order = self._create_order(self.user)
        other = get_user_model().objects.create_user(username='other-user', password='pass12345')
        other_order = self._create_order(other)
        self.client.force_login(self.user)

        response = self.client.get('/accounts/profile/', {'user_id': other.pk})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['display_name'], 'profile-user')
        self.assertContains(response, own_order.code)
        self.assertNotContains(response, other_order.code)

    def test_profile_shows_at_most_20_latest_login_records(self):
        from .models import LoginHistory

        for index in range(21):
            LoginHistory.objects.create(user=self.user, ip_address=f'192.0.2.{index + 1}')
        self.client.force_login(self.user)

        response = self.client.get('/accounts/profile/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['login_history']), 20)

    def test_profile_accepts_valid_avatar_upload(self):
        media_dir = tempfile.TemporaryDirectory()
        self.addCleanup(media_dir.cleanup)
        from django.test import override_settings

        settings_override = override_settings(MEDIA_ROOT=media_dir.name)
        settings_override.enable()
        self.addCleanup(settings_override.disable)
        image_data = BytesIO()
        Image.new('RGB', (1, 1), color='green').save(image_data, format='PNG')
        image_data.seek(0)
        self.client.force_login(self.user)

        response = self.client.post('/accounts/profile/', {
            'avatar': SimpleUploadedFile('avatar.png', image_data.getvalue(), content_type='image/png'),
        })

        self.assertRedirects(response, '/accounts/profile/')
        self.user.profile.refresh_from_db()
        self.assertTrue(self.user.profile.avatar.name.startswith('avatars/'))
        self.assertTrue(self.user.profile.avatar.url.startswith('/media/'))

    def test_profile_rejects_non_image_avatar_upload(self):
        self.client.force_login(self.user)

        response = self.client.post('/accounts/profile/', {
            'avatar': SimpleUploadedFile('avatar.png', b'not-an-image', content_type='image/png'),
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)


class PruneLoginHistoryCommandTests(TestCase):
    def test_command_removes_records_older_than_12_months_and_reports_count(self):
        from django.core.management import call_command, get_commands
        self.assertIn('prune_login_history', get_commands())

        from accounts.management.commands.prune_login_history import retention_cutoff
        from django.utils import timezone

        now = timezone.make_aware(datetime(2026, 10, 24, 12, 0, 0))
        cutoff = retention_cutoff(now)
        user = get_user_model().objects.create_user(username='history-retention', password='pass12345')
        old_record = LoginHistory.objects.create(user=user, ip_address='192.0.2.10')
        boundary_record = LoginHistory.objects.create(user=user, ip_address='192.0.2.11')
        newer_record = LoginHistory.objects.create(user=user, ip_address='192.0.2.12')
        LoginHistory.objects.filter(pk=old_record.pk).update(created_at=cutoff - timedelta(seconds=1))
        LoginHistory.objects.filter(pk=boundary_record.pk).update(created_at=cutoff)
        LoginHistory.objects.filter(pk=newer_record.pk).update(created_at=cutoff + timedelta(days=1))
        output = StringIO()

        with patch('accounts.management.commands.prune_login_history.timezone.now', return_value=now):
            call_command('prune_login_history', stdout=output)

        self.assertFalse(LoginHistory.objects.filter(pk=old_record.pk).exists())
        self.assertTrue(LoginHistory.objects.filter(pk=boundary_record.pk).exists())
        self.assertTrue(LoginHistory.objects.filter(pk=newer_record.pk).exists())
        self.assertIn('1', output.getvalue())
