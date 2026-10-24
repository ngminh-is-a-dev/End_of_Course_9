from django.shortcuts import render
from products.models import Product


def home(request):
    featured_products = Product.objects.select_related('category').filter(
        is_active=True, is_featured=True
    )[:4]
    return render(request, 'core/home.html', {'featured_products': featured_products})


def content_page(request, page):
    titles = {'about': 'Câu chuyện Bean & Leaf', 'contact': 'Liên hệ', 'faq': 'Câu hỏi thường gặp', 'privacy-policy': 'Chính sách bảo mật', 'terms': 'Điều khoản sử dụng', 'return-policy': 'Chính sách đổi trả'}
    return render(request, 'core/content_page.html', {'title': titles.get(page, 'Bean & Leaf'), 'page': page})

# Create your views here.
