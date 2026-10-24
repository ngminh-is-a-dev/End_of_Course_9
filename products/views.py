from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.shortcuts import redirect
from django.templatetags.static import static
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView
from .forms import ProductReviewForm
from .models import Category, Product, ProductReview
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


@method_decorator(login_required, name='post')
class ProductDetailView(DetailView):
    template_name = 'products/product_detail.html'
    queryset = Product.objects.select_related('category').filter(is_active=True)
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reviews = self.object.reviews.select_related('user').order_by('-created_at')
        stats = self.object.reviews.aggregate(average=Avg('rating'), count=Count('id'))
        user_review = None
        if self.request.user.is_authenticated:
            user_review = ProductReview.objects.filter(product=self.object, user=self.request.user).first()
        context.update({
            'reviews': reviews,
            'review_count': stats['count'],
            'review_average': stats['average'],
            'user_review': user_review,
            'review_form': kwargs.get('review_form') or ProductReviewForm(instance=user_review),
            'og_url': self.request.build_absolute_uri(self.object.get_absolute_url()),
            'og_image_url': self.request.build_absolute_uri(
                self.object.image.url if self.object.image else static('images/coffee-hero.png')
            ),
            'zalo_oa_id': getattr(settings, 'ZALO_OA_ID', ''),
        })
        context['related'] = Product.objects.select_related('category').filter(
            category=self.object.category, is_active=True
        ).exclude(pk=self.object.pk)[:4]
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        existing = ProductReview.objects.filter(product=self.object, user=request.user).first()
        form = ProductReviewForm(request.POST, instance=existing)
        if form.is_valid():
            ProductReview.objects.update_or_create(
                product=self.object,
                user=request.user,
                defaults={
                    'rating': form.cleaned_data['rating'],
                    'content': form.cleaned_data['content'],
                },
            )
            messages.success(request, 'Đánh giá của bạn đã được lưu.')
            return redirect(self.object.get_absolute_url())
        return self.render_to_response(self.get_context_data(review_form=form))

# Create your views here.
