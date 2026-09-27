from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from accounts.models import Profile
from orders.models import Order
from products.models import Category, Product


class Command(BaseCommand):
    help = 'Tạo dữ liệu mẫu cho Category, Product, User, Profile và Order.'

    def handle(self, *args, **options):
        categories = {}
        for name, slug in (
            ('Cà phê hạt', 'ca-phe-hat'),
            ('Cà phê xay', 'ca-phe-xay'),
            ('Dụng cụ pha chế', 'dung-cu'),
        ):
            categories[slug], _ = Category.objects.get_or_create(name=name, slug=slug)

        catalogue = (
            ('Cà phê Arabica Cầu Đất', 'ca-phe-arabica-cau-dat', 'ca-phe-hat', 185000, 'Hạt Arabica vị chua thanh nhẹ, hương cam và mật ong.', 25),
            ('Cà phê Robusta Buôn Ma Thuột', 'ca-phe-robusta-buon-ma-thuot', 'ca-phe-hat', 150000, 'Hậu vị chocolate đậm đà, phù hợp pha phin.', 30),
            ('Cà phê xay Espresso', 'ca-phe-xay-espresso', 'ca-phe-xay', 165000, 'Mẻ rang đậm, thơm dày và giàu crema.', 20),
            ('Bộ pha V60 thủy tinh', 'bo-pha-v60-thuy-tinh', 'dung-cu', 320000, 'Bộ dụng cụ tối giản cho pour-over tại nhà.', 10),
        )
        for name, slug, category, price, description, stock in catalogue:
            Product.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'category': categories[category],
                    'price': price,
                    'description': description,
                    'stock': stock,
                    'is_active': True,
                },
            )

        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username='demo',
            defaults={'email': 'demo@example.com', 'first_name': 'Người dùng'},
        )
        if created:
            user.set_password('demo12345')
            user.save(update_fields=['password'])

        profile, _ = Profile.objects.get_or_create(
            user=user,
            defaults={'phone': '0900000000', 'address': 'Hà Nội'},
        )
        Order.objects.update_or_create(
            code='DH-DEMO-001',
            defaults={
                'user': user,
                'customer_name': user.get_full_name() or user.username,
                'email': user.email,
                'phone': profile.phone,
                'address': profile.address,
                'total': 335000,
                'status': Order.CONFIRMED,
                'note': 'Đơn hàng mẫu để kiểm tra admin',
            },
        )
        self.stdout.write(self.style.SUCCESS('Created sample data: 3 categories, 4 products, 1 user/profile, and 1 order.'))
