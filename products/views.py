from django.views.generic import DetailView, ListView
from .models import Category, Product
from .selectors import get_filtered_products


class ProductListView(ListView):
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        return get_filtered_products(self.request.GET)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['roasts'] = Product.ROAST_CHOICES
        context['selected_categories'] = self.request.GET.getlist('category')
        context['selected_roasts'] = self.request.GET.getlist('roast')
        return context


class ProductDetailView(DetailView):
    template_name = 'products/product_detail.html'
    queryset = Product.objects.select_related('category').filter(is_active=True)
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related'] = Product.objects.filter(category=self.object.category, is_active=True).exclude(pk=self.object.pk)[:4]
        return context

# Create your views here.
