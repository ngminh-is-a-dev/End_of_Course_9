from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from products.models import Product
from .services import VOUCHER_SESSION_KEY, add_product, cart_summary, set_quantity

def cart_detail(request):
    return render(request, 'cart/detail.html', cart_summary(request.user, request.session))

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    next_url = request.POST.get('next', '')
    if not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = reverse('cart:detail')
    if request.method == 'POST':
        try:
            quantity = max(1, int(request.POST.get('quantity', 1)))
        except (TypeError, ValueError):
            messages.error(request, 'Số lượng không hợp lệ.')
            return redirect(next_url)
        if product.stock <= 0:
            set_quantity(request.session, product.id, 0)
            messages.error(request, 'Sản phẩm đã hết hàng.')
            return redirect(next_url)
        previous_quantity = request.session.get('bean_leaf_cart', {}).get(str(product.id), 0)
        add_product(request.session, product.id, quantity, stock=product.stock)
        if previous_quantity + quantity > product.stock:
            messages.warning(request, 'Số lượng trong giỏ đã được giới hạn theo tồn kho hiện tại.')
        else:
            messages.success(request, f'Đã thêm {product.name} vào giỏ hàng.')
    return redirect(next_url)

def update_cart(request, product_id):
    if request.method == 'POST':
        try:
            quantity = max(0, int(request.POST.get('quantity', 0)))
        except (TypeError, ValueError):
            messages.error(request, 'Số lượng không hợp lệ.')
            return redirect('cart:detail')
        product = Product.objects.filter(pk=product_id, is_active=True).first()
        if product is None or product.stock <= 0:
            set_quantity(request.session, product_id, 0)
            messages.error(request, 'Sản phẩm đã hết hàng và được gỡ khỏi giỏ.')
        else:
            if quantity > product.stock:
                messages.warning(request, 'Số lượng trong giỏ đã được giới hạn theo tồn kho hiện tại.')
            set_quantity(request.session, product_id, quantity, stock=product.stock)
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
