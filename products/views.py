from django.views.generic import DetailView, ListView

from .models import Category, Product
from .selectors import get_filtered_products


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        return get_filtered_products(self.request.GET)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['roasts'] = Product.ROAST_CHOICES
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.select_related('category').filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        context['related'] = (
            Product.objects.select_related('category')
            .filter(is_active=True, category=product.category)
            .exclude(pk=product.pk)[:4]
        )
        return context
