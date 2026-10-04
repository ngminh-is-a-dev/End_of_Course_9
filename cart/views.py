from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from products.models import Product
from .services import VOUCHER_SESSION_KEY, add_product, cart_summary, set_quantity


def _quantity_from_request(request, default=1):
    try:
        return int(request.POST.get('quantity', default))
    except (TypeError, ValueError):
        return default

def cart_detail(request):
    return render(request, 'cart/detail.html', cart_summary(request.user, request.session))

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    if request.method == 'POST':
        if product.stock <= 0:
            messages.error(request, f'{product.name} hiện đã hết hàng.')
            return redirect('products:detail', slug=product.slug)
        quantity = _quantity_from_request(request)
        add_product(request.session, product.id, quantity, product.stock)
        messages.success(request, f'Đã thêm {product.name} vào giỏ hàng.')
    next_url = request.POST.get('next', '')
    if not url_has_allowed_host_and_scheme(next_url, {request.get_host()}, request.is_secure()):
        next_url = reverse('cart:detail')
    return redirect(next_url)

def update_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        set_quantity(request.session, product_id, _quantity_from_request(request, 0), product.stock)
    return redirect('cart:detail')


def apply_voucher(request):
    if request.method != 'POST':
        return redirect('cart:detail')
    if not request.user.is_authenticated:
        messages.info(request, 'Hãy đăng ký hoặc đăng nhập để nhận voucher miễn phí vận chuyển.')
        return redirect('accounts:signup')
    voucher = request.user.vouchers.filter(code=request.POST.get('code', '').strip().upper(), is_used=False).first()
    if voucher:
        request.session[VOUCHER_SESSION_KEY] = voucher.code
        request.session.modified = True
        messages.success(request, f'Đã áp dụng voucher {voucher.code}: miễn phí vận chuyển.')
    else:
        messages.error(request, 'Voucher không hợp lệ hoặc đã được sử dụng.')
    return redirect('cart:detail')


def remove_voucher(request):
    if request.method == 'POST':
        request.session.pop(VOUCHER_SESSION_KEY, None)
        request.session.modified = True
        messages.info(request, 'Đã gỡ voucher khỏi đơn hàng.')
    return redirect('cart:detail')

# Create your views here.
