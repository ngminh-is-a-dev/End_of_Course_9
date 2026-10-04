from django.core.management.base import BaseCommand
from products.models import Category, Product


class Command(BaseCommand):
    help = 'Creates a small Bean & Leaf demo catalogue.'

    def handle(self, *args, **options):
        categories = {}
        for name, slug in [('Cà phê hạt', 'ca-phe-hat'), ('Cà phê xay', 'ca-phe-xay'), ('Dụng cụ pha chế', 'dung-cu')]:
            categories[slug], _ = Category.objects.get_or_create(name=name, slug=slug)
        catalogue = [
            ('Cà Phê Laura Coffee Blend Xám', 'laura-coffee-blend-xam', 'ca-phe-hat', 150000, 'dark', 'Đà Lạt, Việt Nam', 'Hậu vị chocolate, đậm đà và cân bằng. Phù hợp cho espresso hoặc phin truyền thống.', True),
            ('Cà Phê Mộc Cầu Đất', 'ca-phe-moc-cau-dat', 'ca-phe-hat', 185000, 'medium', 'Cầu Đất, Lâm Đồng', 'Hạt Arabica có vị chua thanh nhẹ, điểm xuyết hương cam và mật ong.', True),
            ('Espresso House Blend', 'espresso-house-blend', 'ca-phe-xay', 165000, 'dark', 'Buôn Ma Thuột, Việt Nam', 'Mẻ rang đậm dành riêng cho những ly espresso thơm dày, giàu crema.', True),
            ('Cold Brew Daily', 'cold-brew-daily', 'ca-phe-xay', 135000, 'medium', 'Lâm Đồng, Việt Nam', 'Cà phê xay cho cold brew, hương cacao dịu và hậu vị sạch.', True),
            ('Bộ pha V60 thủy tinh', 'bo-pha-v60-thuy-tinh', 'dung-cu', 320000, 'light', 'Nhật Bản', 'Bộ dụng cụ tối giản để bắt đầu hành trình pour-over tại nhà.', False),
            ('Bình French Press', 'binh-french-press', 'dung-cu', 265000, 'medium', 'Pháp', 'French press 350 ml cho tách cà phê trọn vị và ấm áp.', False),
            ('Cà Phê Đắk Lắk Honey', 'ca-phe-dak-lak-honey', 'ca-phe-hat', 205000, 'light', 'Đắk Lắk, Việt Nam', 'Hương trái cây chín và mật ngọt tự nhiên, rang sáng.', False),
            ('Cà Phê Phin Truyền Thống', 'ca-phe-phin-truyen-thong', 'ca-phe-xay', 120000, 'dark', 'Việt Nam', 'Vị đắng dịu, thơm nồng, dành cho nghi thức cà phê phin mỗi sáng.', False),
        ]
        for name, slug, category, price, roast, origin, description, featured in catalogue:
            Product.objects.update_or_create(slug=slug, defaults={'name': name, 'category': categories[category], 'price': price, 'roast_level': roast, 'origin': origin, 'description': description, 'is_featured': featured, 'stock': 25})
        self.stdout.write(self.style.SUCCESS(f'Created {len(catalogue)} demo products.'))
