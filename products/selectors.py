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
    if price == 'under-150':
        products = products.filter(price__lt=150000)
    elif price == '150-300':
        products = products.filter(price__range=(150000, 300000))
    elif price == 'over-300':
        products = products.filter(price__gt=300000)
    return products
