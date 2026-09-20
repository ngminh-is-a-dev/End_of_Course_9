from rest_framework import generics
from rest_framework.filters import SearchFilter
from .models import Product
from .serializers import ProductSerializer


class ProductApiListView(generics.ListAPIView):
    """Read-only catalogue API with search and category/roast query filters."""
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name', 'description', 'origin']

    def get_queryset(self):
        products = Product.objects.select_related('category').filter(is_active=True)
        category = self.request.query_params.get('category')
        roast = self.request.query_params.get('roast')
        if category:
            products = products.filter(category__slug=category)
        if roast:
            products = products.filter(roast_level=roast)
        return products


class ProductApiDetailView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    queryset = Product.objects.select_related('category').filter(is_active=True)
