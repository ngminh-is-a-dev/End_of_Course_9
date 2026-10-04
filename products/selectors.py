from django.db.models import Q
from .models import Product


def get_filtered_products(params):
    products = Product.objects.select_related('category').filter(is_active=True)
    query = params.get('q', '').strip()
    categories = params.getlist('category')
    roasts = params.getlist('roast')
    price = params.get('price', '')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if categories:
        products = products.filter(category__slug__in=categories)
    if roasts:
        products = products.filter(roast_level__in=roasts)
    ranges = {'under-150': (0, 150000), '150-300': (150000, 300000), 'over-300': (300000, 99999999)}
    if price in ranges:
        products = products.filter(price__range=ranges[price])
    return products
